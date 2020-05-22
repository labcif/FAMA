import argparse
import logging
import os
import glob
import sys

debug = False

class MDLFixer:
    @staticmethod
    def folder_scanner(base_path = sys.path[0]):
        files = []
        for filename in glob.glob(os.path.join(base_path, "*.mdl")):
            if os.stat(filename).st_size > 0:
                filepath = MDLFixer.generator(filename)
                if filepath:
                    files.append(filepath)
        return files


    @staticmethod
    def generator(filename):
        if not filename.endswith('.mdl'):
            if debug:
                logging.error("File extension must be .mdl. {}".format(filename))
            return None

        videokey = filename.split('_')[0]
        nodeconfs = glob.glob("{}*.mdlnodeconf".format(videokey))

        header = b""
        for node in nodeconfs:
            header = MDLFixer.find_header(node)
            if header:
                break

        if not header:
            if debug:
                logging.error("No valid .mdlnodeconf found for {}".format(filename))

            if '_h264_' in filename:
                header = b'\x00\x00\x00 ftypisom\x00\x00\x02\x00isomiso2avc1mp41\x00\x00M\xfbmoov\x00\x00\x00lmvhd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xe8\x00\x00B\xda\x00\x01'
            elif '_h265_' in filename:
                header = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00o\xfamoov\x00\x00\x00lmvhd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xe8\x00\x00\x81'\x00\x01"
            else:
                if debug:
                    logging.error("Unable to identify the codec")

                return None

        return MDLFixer.generate_file(filename, header)

    @staticmethod
    def find_header(filename):
        file = open(filename, "rb")
        
        contents = file.read()
        typeposition = contents.find(b'ftyp')
        if typeposition < 4: #ignore this back logic
            return b""

        #Header starting position is variable so we find ftyp and we go back -4 (emulating the original file)
        file.seek(typeposition - 4)

        cont = True
        header = b""
        while cont:
            byte = file.read(1)
            header += byte

            #In the H264 format the byte stream is organised into many NAL unit. In order to understand where a NAL unit starts a three-byte or four-byte start code, 0x000001 or 0x00000001, is placed at the beginning of each NAL unit.
            #https://stackoverflow.com/questions/38094302/how-to-understand-header-of-h264
            #We are looking until 01
            if byte == b'\x01':
                cont = False

            if not byte: #not the file we want
                header = b""
                cont = False

        return header

    @staticmethod
    def generate_file(filename, header):
        videofilename = filename.replace('.mdl', '.mp4')

        with open(videofilename, 'wb') as outfile, open(filename, 'rb') as infile:
            #write header!
            outfile.write(header)

            #seek input header size
            infile.seek(len(header))

            #write remaining
            outfile.write(infile.read())

        if debug:
            logging.info("File generated at {}".format(videofilename))
            
        return videofilename

if __name__ == "__main__":
    log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    parser = argparse.ArgumentParser(description='TikTok Cache V2 MDL')
    parser.add_argument('-i', '--input', help='<filename.mdl>', required = False)
    args = parser.parse_args()

    if args.input:
        MDLFixer.generator(args.input)
    else:
        MDLFixer.folder_scanner()