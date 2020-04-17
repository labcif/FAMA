#sqlparse.py
#FORKED FROM https://github.com/mdegrazia/SQLite-Deleted-Records-Parser WITH PYTHON2/3 COMPATIBILITY AND IMPROVEMENTS
#
#This program parses an SQLite3 database for deleted entires and
#places the output into either and TSV file, or text file
#
#The SQLite file format, offsets etc is described at
#sqlite.org/fileformat.html
#
#
# Copyright (C) 2015 Mari DeGrazia (arizona4n6@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>
#
# Version History:
# v1.1 2013-11-05
#
# v1.2 2015-06-20
#support added in to print out non b-tree pages
#
# v.1.3 2015-06-21
#minor changes / comments etc.
# 
#		
#Find a bug???? Please let me know and I'll try to fix it (if you ask nicely....)
#

import struct
import logging
from optparse import OptionParser
import sys
import re
import os

from package.utils import Utils

class SQLParse:
    @staticmethod
    def remove_ascii_non_printable(chunk):
        try: #py3
            chunk = ''.join(map(chr, chunk))
        except: #py2
            chunk = ' '.join(chunk.split())

        return ''.join([ch for ch in chunk if ord(ch) > 31 and ord(ch) < 126 or ord(ch) ==9])

    @staticmethod
    def read_contents(path):
        listing = []
        options = {
            "raw": False,
            "printpages": True
        }
        #open file, confirm it is an SQLite DB
        try:
            f = open(path,"rb")
        except:
            return None

        #get the file size, we'll need this later
        #filesize = len(f.read())
        # Cheeky suggestion ... so it doesnt read the whole file unecessarily
        
        if not Utils.verify_header_signature(path, header_type = b"SQLite", offset = 0):
            logging.error("File does not appear to be an SQLite File")
            return None
    
        stats = os.stat(path)
        filesize = stats.st_size

        f.seek(0)

        #OK, lets get started. The SQLite database is made up of multiple Pages. We need to get the size of each page.
        #The pagesize this is stored at offset 16 at is 2 bytes long

        pagesize = struct.unpack('>H', f.read(2))[0]

        #According to SQLite.org/fileformat.html,  all the data is contained in the table-b-trees leaves.
        #Let's go to each Page, read the B-Tree Header, and see if it is a table b-tree, which is designated by the flag 13

        #set the offset to 0, so we can also process any strings in the first page
        offset = 0

        #while the offset is less then the filesize, keep processing the pages

        while offset < filesize: 
            
            #move to the beginning of the page and read the b-tree flag, if it's 13, its a leaf table b tree and we want to process it
            f.seek(offset)
            flag = struct.unpack('>b',f.read(1))[0]
            
            if flag == 13:
                
                #this is a table_b_tree - get the header information which is contained in the first 8 bytes
                
                freeblock_offset = struct.unpack('>h',f.read(2))[0] 
                num_cells = struct.unpack('>h',f.read(2))[0]
                cell_offset = struct.unpack('>h',f.read(2))[0]
                num_free_bytes = struct.unpack('>b',f.read(1))[0]
                
                
                #unallocated is the space after the header information and before the first cell starts 
                
                #start after the header (8 bytes) and after the cell pointer array. The cell pointer array will be the number of cells x 2 bytes per cell
                start = 8 + (num_cells * 2)
                
                # the length of the unallocated space will be the difference between the start and the cell offset
                length = cell_offset-start
                
                #move to start of unallocated, then read the data (if any) in unallocated - remember, we already read in the first 8 bytes, so now we just need to move past the cell pointer array
                f.read(num_cells*2)
                unallocated = f.read(length)
                
                item = {}
                item["offset"] = str(offset+start)
                item["length"] = str(length)

                if options["raw"] == True:
                    item["unallocated"] = unallocated
                    listing.append(item)
                else:
                #lets clean this up so its mainly the strings - remove white spaces and tabs too
                    
                    unallocated  = SQLParse.remove_ascii_non_printable(unallocated )
                    if unallocated != "":
                        item["unallocated"] = re.sub('\s+',' ', str(unallocated))
                        listing.append(item)
                        
                #if there are freeblocks, lets pull the data
                
                while freeblock_offset != 0:
                    
                    #move to the freeblock offset
                    f.seek(offset+freeblock_offset)
                    
                    #get next freeblock chain
                    next_fb_offset = struct.unpack('>h',f.read(2))[0]
                
                    #get the size of this freeblock
                    free_block_size = struct.unpack('>hh',f.read(4))[0]
                    
                    #move to the offset so we can read the free block data
                    f.seek(offset+freeblock_offset)
                    
                    #read in this freeblock
                    free_block = f.read(free_block_size)
                    
                    item = {}
                    item["offset"] = str(offset+freeblock_offset)
                    item["length"] = str(free_block_size)

                    if options["raw"] == True:
                        item["freeblock"] = free_block
                        listing.append(item)
                    else:
                        #lets clean this up so its mainly the strings - remove white spaces and tabs too
                        free_block  = SQLParse.remove_ascii_non_printable(free_block)
                        if unallocated != "":
                            item["freeblock"] = re.sub('\s+',' ', str(free_block))
                            listing.append(item)
                    
                    freeblock_offset = next_fb_offset
                
            # Cheeky's Change: Extract strings from non-Leaf-Table B-tree pages to handle re-purposed/re-used pages 
            # According to docs, valid flag values are 2, 5, 10, 13 BUT pages containing string data have also been observed with flag = 0
            # So just print strings from all non flag = 13 pages. 
            elif (options["printpages"]):
                # read block into one big string, filter unprintables, then print
                pagestring = f.read(pagesize-1) # we've already read the flag byte
                printable_pagestring = SQLParse.remove_ascii_non_printable(pagestring)
                
                item = {}
                item["type"] = "Non-Leaf-Table-Btree-Type_" + str(flag)
                item["offset"] = str(offset)
                item["length"] = str(pagesize)

                if options["raw"] == True:
                    item["data"] = printable_pagestring
                else:
                    item["data"] = re.sub('\s+',' ', printable_pagestring)
                
                listing.append(item)

            #increase the offset by one pagesize and loop
            offset = offset + pagesize

        return listing
            
#end

