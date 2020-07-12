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
        self.external_data_path = "/sdcard/Android/data/{}"
        self.internal_data_dump_name = "{}_internal.tar.gz"
        self.external_data_dump_name = "{}_external.tar.gz"

        #Dump internal data https://android.stackexchange.com/questions/85564/need-one-line-adb-shell-su-push-pull-to-access-data-from-windows-batch-file
        self.check_root_command = """'{}' -s {} shell "su -c 'echo HASROOT'" """
        self.magic_root_command = """'{}' -s {} shell "su -c 'cd {} && tar czf - ./ --exclude='./files' | base64' 2>/dev/null" | {} -d"""
        self.magic_noroot_command = """'{}' -s {} shell "cd {} && tar czf - ./ --exclude='./files' | base64 2>/dev/null" | {} -d"""

        if not (Utils.get_platform().startswith("windows") or Utils.get_platform().startswith("darwin")): #some linux versions doesn't output if contains errors, so we ignore it. but base64 for windows doesn't have this attribute
            self.magic_root_command += "i" #add -i flag to base64 decode to avoid some encoding issues
            self.magic_noroot_command += "i" #add -i flag to base64 decode to avoid some encoding issues

        self.adb_location = Utils.get_adb_location()
        self.base64_location = Utils.get_base64_location()

        self.dumps_path = os.path.join(Utils.get_base_path_folder(), "dumps")
        Utils.check_and_generate_folder(self.dumps_path)
        
        self.path_dump_folder = os.path.join(self.dumps_path, Utils.get_current_time())
    
    def dump_from_adb(self, app_package, devices = None):
        if not devices:
            devices = DeviceCommunication.list_devices()

        folders = {}

        Utils.check_and_generate_folder(self.path_dump_folder)

        for serial_number in devices:
            path_dump_folder = os.path.join(self.path_dump_folder, Utils.clean_invalid_filename(serial_number, character="_"))
            Utils.check_and_generate_folder(path_dump_folder)

            root_status = self.check_root_access(serial_number)

            if root_status:
                #Dump internal
                logging.info("[{}] Extracting internal {} (root) data!".format(serial_number, app_package))
                path_dump_internal = os.path.join(path_dump_folder, self.internal_data_dump_name.format(app_package))
                self.extract_from_device(serial_number, root_status, self.internal_data_path.format(app_package), path_dump_internal)

            #Dump external
            logging.info("[{}] Extracting external {} data!".format(serial_number, app_package))
            path_dump_external = os.path.join(path_dump_folder, self.external_data_dump_name.format(app_package))
            self.extract_from_device(serial_number, root_status, self.external_data_path.format(app_package), path_dump_external)

            #Dump output folder
            folders[serial_number] = path_dump_folder
        
        return folders

    def check_root_access(self, serial_number):
        output = str(subprocess.Popen(self.check_root_command.format(self.adb_location, serial_number), shell=True, stdout=subprocess.PIPE, stderr=None).stdout.read())
        status = "HASROOT" in output
        logging.info("[{}] Root status: {}".format(serial_number, status))
        return status

    def extract_from_device(self, serial_number, root_status, path_to_extract, output_path):
        sort_out = open(output_path, 'wb', 0)

        if root_status:
            command = self.magic_root_command.format(self.adb_location, serial_number, path_to_extract, self.base64_location)
        else:
            command = self.magic_noroot_command.format(self.adb_location, serial_number, path_to_extract, self.base64_location)

        subprocess.Popen(command, shell=True, stdout=sort_out, stderr=None).wait()
        sort_out.close()

        #Clean the file if it's empty
        if os.path.getsize(output_path) == 0:
            logging.warning("[{}] Nothing extracted!".format(serial_number))
            try:
                os.remove(output_path)
            except:
                pass
        else:
            logging.info("[{}] File generated! {}".format(serial_number, output_path))