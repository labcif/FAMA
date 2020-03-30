import os
import sys
import csv
import platform
import tarfile
import xml.etree.ElementTree as ET
import datetime
import subprocess
import shutil

#from meaning.meaning import Meaning
#from database import DatabaseParser

class Utils:
    ### TAR UTILS

    @staticmethod
    def get_base_path_folder():
        return os.path.dirname(__file__)

    @staticmethod
    def generate_tar_gz_file(folder_path, generated_file_path):
        arcname = os.path.basename(generated_file_path).replace('.tar.gz', '')
        with tarfile.open(generated_file_path, mode='w:gz') as archive:
            archive.add(folder_path, recursive=True, arcname = arcname)
    
    @staticmethod
    def list_files_tar(file_path, filter_type = None):
        files_list = []
        if not file_path or not os.path.exists(file_path):
            return files_list
            
        tar = tarfile.open(file_path)
        for member in tar.getmembers():
            path = member.name
            if filter_type:
                extension = os.path.splitext(path)[1].strip().lower()
                if not extension in filter_type:
                    if extension != "": 
                        continue

                    if not member.isfile():
                        continue
                    
                    if not ".db" or ".mp4" in filter_type: #we are only checking header for sqlite for now
                        continue

                    if not Utils.verify_header_signature(path, header_type = b"SQLite", offset = 0, stream = tar.extractfile(member)):
                        continue

            files_list.append(path)

        tar.close()
        return files_list
    
    @staticmethod
    def extract_file_tar(file_path, file_member, cache_path):
        if not file_path or not os.path.exists(file_path):
            return False

        Utils.check_and_generate_folder(os.path.dirname(cache_path))
        with tarfile.open(file_path) as tar:
            fileobj = tar.extractfile(file_member)
            with open(cache_path, 'wb') as savefile:
                savefile.write(fileobj.read())
            fileobj.close()
        return True

    @staticmethod
    def list_files(folder_name, filter_type = None):
        files_list = []
        if not folder_name or not os.path.exists(folder_name):
            return files_list

        for root, _, files in os.walk(os.path.join(Utils.get_base_path_folder(), folder_name)):
            for file in files:
                if filter_type:
                    extension = os.path.splitext(file)[1].strip().lower()
                    if not extension in filter_type:
                        if extension != "": #ignore files with extension
                            continue

                        if not ".db" in filter_type: #we are only checking header for sqlite for now
                            continue
                        
                        #verify sqlite files with extension
                        if not Utils.verify_header_signature(os.path.join(root, file), header_type = b"SQLite", offset = 0):
                            continue

                files_list.append(os.path.join(root, file))
        
        return files_list
    @staticmethod
    def get_current_time():
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    

    

    '''
    @staticmethod
    def export_columns_from_database(folder_path):
        meaning = Meaning()
        path = os.path.join(folder_path, 'DumpColumns.csv')
        print("[Utils] Dumping Columns to CSV. Base path {}".format(path))
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['database', 'table', 'column', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
            for db in Utils.list_files(folder_path, filter_type = [".db"]):
                database_name = db.split("/")[-1]
                for table, columns in DatabaseParser.dump_columns(database = db).items():
                    meanings = meaning.get_meaning(database_name, table)
                    item = {}
                    item["database"] = db.replace(folder_path, '') #remove basepath
                    item["table"] = table
                    
                    for column in columns:
                        item["column"] = column
                        if meanings:
                            item["description"] = meanings.get(column)

                        writer.writerow(item)
    '''
    @staticmethod
    def verify_header_signature(file, header_type, offset, stream = None):
        header = b""
        if stream:
            header = stream.read(32)
        else:
            with open(file, "rb") as f:
                header = f.read(32)

        query = header.find(header_type) #query includes position of header

        return True if query == offset else False

    @staticmethod
    def xml_attribute_finder(xml_path, attrib_values = None):
        listing = {}
        if not os.path.exists(xml_path):
            return None
            
        root = ET.parse(xml_path).getroot()
        for child in root:
            if not attrib_values or child.attrib.get("name") in attrib_values: #all values or specific value
                if child.attrib.get("value"):
                    value= child.attrib.get("value")
                else:
                    value = child.text

                try:
                    listing[child.attrib.get("name")] = str(value)
                except:
                    listing[child.attrib.get("name")] = "ERROR"
        return listing

    @staticmethod
    def check_and_generate_folder(path):
        if not os.path.exists(path):
            return os.makedirs(path)

        return True

    @staticmethod
    def replace_slash_platform(path):
        if platform.system() == "Windows":
            return path.replace('/', '\\')
        
        return path.replace('\\', '/')

    
    @staticmethod
    def check_string_in_string_list(string, listing):
        return any(string in s for s in listing)

    @staticmethod
    def get_adb_location():
        if platform.system() == "Windows":
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "windows", "adb.exe")
        elif platform.system() == "Darwin":
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "mac", "adb")
        else:
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "linux", "adb")
    @staticmethod
    def get_undark_location():
        if platform.system() == "Windows":
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "windows", "undark.exe")
        elif platform.system() == "Darwin":
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "mac", "undark")
        else:
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "linux", "undark")


    @staticmethod
    def get_base64_location():
        if platform.system() == "Windows":
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "windows", "base64.exe")
        else:
            return "base64"

    @staticmethod
    def run_undark(db):
        undark = Utils.get_undark_location()
        return subprocess.Popen([undark,'-i', db, '--freespace'], shell=True, stdout=subprocess.PIPE).stdout.read()

    @staticmethod
    def remove_folder(folder):
        shutil.rmtree(folder)


# if __name__ == "__main__":
#     a = Utils.run_undark("6793838184616526854_im.db")
#     print(a)
 




#print(Utils.xml_attribute_finder("/Users/Nogueira/MEOCloud/ProjetoFinal/ProjetoPython/output/H7AZCY02B588KZL/20200301_21h20m24s/com.zhiliaoapp.musically-v15.0.1/internal/shared_prefs/aweme_account_terminal_relative_sp.xml", "account_terminal_app_has_logged_out"))