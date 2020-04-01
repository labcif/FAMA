import subprocess

from utils import Utils

class DeviceCommunication:
    def __init__(self):
        self.devices = []

    def list_devices(self):
        print("[ADB] Getting list of devices")
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

            devices.append(device_serial)
            
        message = "Found {} device".format(len(devices))
        if (len(devices) != 1):
            message += "s"
            
        print("[ADB] {}".format(message))
        return devices


