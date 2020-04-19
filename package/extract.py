import subprocess
import datetime
import os
import sys
import logging

from package.utils import Utils
from package.device import DeviceCommunication

class Extract:
    def __init__(self):
        self.internal_data_path = "/data/data/{}"
        self.external_data_path = "/data/media/0/Android/data/{}"
        self.internal_data_dump_name = "{}_internal.tar.gz"
        self.external_data_dump_name = "{}_external.tar.gz"

        if Utils.get_platform().startswith("windows") or Utils.get_platform().startswith("darwin"): #some linux versions doesn't output if contains errors, so we ignore it. but base64 for windows doesn't have this attribute
            self.ignore_attribute = ""
        else:
            self.ignore_attribute = "i"

        self.dumps_path = os.path.join(Utils.get_base_path_folder(), "dumps")

        Utils.check_and_generate_folder(self.dumps_path)

    def dump_from_adb(self, app_package):
        folders = {}

        device_communication = DeviceCommunication()
        for serial_number in device_communication.list_devices():
            current_time = Utils.get_current_time()
            path_dump_folder = os.path.join(self.dumps_path, current_time)
            path_dump_internal = os.path.join(path_dump_folder, self.internal_data_dump_name.format(app_package))
            path_dump_external = os.path.join(path_dump_folder, self.external_data_dump_name.format(app_package))

            adb_location = Utils.get_adb_location()
            base64_location = Utils.get_base64_location()

            #Check if we have dump folder
            Utils.check_and_generate_folder(path_dump_folder)
            
            #Dump internal data https://android.stackexchange.com/questions/85564/need-one-line-adb-shell-su-push-pull-to-access-data-from-windows-batch-file
            
            
            logging.info("[{}] Extracting internal app (root) data!".format(serial_number))

            sort_out = open(path_dump_internal, 'wb', 0)
            command = """{} -s {} shell "su -c 'cd {} && tar czf - ./ --exclude='./files'| base64' 2>/dev/null" | {} -d{}""".format(adb_location, serial_number, self.internal_data_path.format(app_package), base64_location, self.ignore_attribute)
            subprocess.Popen(command, shell=True, stdout=sort_out).wait()

            #Clean the file if it's empty
            if os.path.getsize(path_dump_internal) == 0:
                logging.warning("[{}] Nothing extracted!".format(serial_number))
                try:
                    os.remove(path_dump_internal)
                except:
                    pass
            else:
                logging.info("[{}] File generated! {}".format(serial_number, path_dump_internal))

            #Dump external
            logging.info("[{}] Extracting external app data!".format(serial_number))
            
            sort_out = open(path_dump_external, 'wb', 0)
            command = """{} -s {} shell "su -c 'cd {} && tar czf - ./ | base64' 2>/dev/null" | {} -d{}""".format(adb_location, serial_number, self.external_data_path.format(app_package), base64_location, self.ignore_attribute)
            subprocess.Popen(command, shell=True, stdout=sort_out).wait()
            
            if os.path.getsize(path_dump_external) == 0:
                logging.warning("[{}] Nothing extracted!".format(serial_number))
                try:
                    os.remove(path_dump_external)
                except:
                    pass
            else:
                logging.info("[{}] File generated! {}".format(serial_number, path_dump_external))

            #Generated folders
            #folders.append(path_dump_folder)
            folders[serial_number] = path_dump_folder
        
        return folders