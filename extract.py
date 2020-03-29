import subprocess
import datetime
import os
import sys

from utils import Utils
from device import DeviceCommunication

class Extract:
    def __init__(self):
        self.internal_data_path = "/data/data/{}"
        self.external_data_path = "/sdcard/Android/data/{}"
        self.internal_data_dump_name = "{}_internal.tar.gz"
        self.external_data_dump_name = "{}_external.tar.gz"

        self.dumps_path = os.path.join(sys.path[0], "dumps")

        Utils.check_and_generate_folder(self.dumps_path)

    def dump_from_adb(self, app_package):
        folders = []

        device_communication = DeviceCommunication()
        for device in device_communication.list_devices():
            serial_number = device.get_serial_no()

            current_time = Utils.get_current_time()
            path_dump_folder = os.path.join(self.dumps_path, current_time)
            path_dump_internal = os.path.join(path_dump_folder, self.internal_data_dump_name.format(app_package))
            path_dump_external = os.path.join(path_dump_folder, self.external_data_dump_name.format(app_package))

            adb_location = Utils.get_adb_location()
            base64_location = Utils.get_base64_location()

            #Check if we have dump folder
            Utils.check_and_generate_folder(path_dump_folder)
            
            #Dump internal data https://android.stackexchange.com/questions/85564/need-one-line-adb-shell-su-push-pull-to-access-data-from-windows-batch-file
            print("[{}] Extracting internal app (root) data!".format(serial_number))

            command = """{} -s {} shell "su -c 'cd {} && tar czf - ./ --exclude='./files'| base64' 2>/dev/null" | {} -d > {}""".format(adb_location, serial_number, self.internal_data_path.format(app_package), base64_location, path_dump_internal)
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

            #Clean the file if it's empty
            if os.path.getsize(path_dump_internal) == 0:
                print("[{}] Nothing extracted!".format(serial_number))
                try:
                    os.remove(path_dump_internal)
                except:
                    pass
            else:
                print("[{}] File generated! {}".format(serial_number, path_dump_internal))

            #Dump external
            print("[{}] Extracting external app data!".format(serial_number))

            command = """{} -s {} shell "su -c 'cd {} && tar czf - ./ | base64' 2>/dev/null" | {} -d > {}""".format(adb_location, serial_number, self.external_data_path.format(app_package), base64_location, path_dump_external)
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
            
            if os.path.getsize(path_dump_external) == 0:
                print("[{}] Nothing extracted!".format(serial_number))
                try:
                    os.remove(path_dump_external)
                except:
                    pass
            else:
                print("[{}] File generated! {}".format(serial_number, path_dump_external))

            #Generated folders
            folders.append(path_dump_folder)
        
        return folders

    def dump_from_path(self, base_path, app_package):
        base_path = Utils.replace_slash_platform(base_path)

        if not os.path.exists(base_path):
            print("[Dump] Dump from path failed: {} doesn't exists".format(base_path))
            return None

        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path_dump_folder = os.path.join(self.dumps_path, current_time)
        path_dump_internal = os.path.join(path_dump_folder, self.internal_data_dump_name.format(app_package))
        path_dump_external = os.path.join(path_dump_folder, self.external_data_dump_name.format(app_package))
        
        #Check if we have dump folder
        Utils.check_and_generate_folder(path_dump_folder)

        #Extract internal data from mount
        path_original_internal = Utils.replace_slash_platform(os.path.join(base_path, self.internal_data_path.format(app_package)[1:])) #clean first / to allow concat
        if os.path.exists(path_original_internal):
            print("[Dump] Extracting internal app data!")
            Utils.generate_tar_gz_file(path_original_internal, path_dump_internal)
        else:
            print("[Dump] Internal app folder {} doesn't exist".format(path_original_internal))

        #Extract external data from mount
        path_original_external = Utils.replace_slash_platform(os.path.join(base_path, self.external_data_path.format(app_package)[1:]))
        if os.path.exists(path_original_external):
            print("[Dump] Extracting external app data!")
            Utils.generate_tar_gz_file(path_original_external, path_dump_external)
        else:
            print("[Dump] External app folder {} doesn't exist".format(path_original_external))        

        return [path_dump_folder]