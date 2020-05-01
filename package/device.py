import subprocess
import logging

from package.utils import Utils

class DeviceCommunication:
    @staticmethod
    def list_devices():
        logging.info("Getting list of devices")
        adb_location = Utils.get_adb_location()
        command = """{} devices""".format(adb_location)
        info = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

        devices = []

        for device in info.decode().splitlines():
            if 'devices attached' in device:
                continue

            device_serial = device.split('\t')[0].strip()

            if not device_serial:
                continue
            
            if '\tunauthorized' in device:
                logging.warning("{} unauthorized. Trust this device. Ignoring...".format(device_serial))
                continue

            devices.append(device_serial)
            
        message = "Found {} device".format(len(devices))
        if (len(devices) != 1):
            message += "s"
            
        logging.info("{}".format(message))
        return devices


