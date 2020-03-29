from ppadb.client import Client as AdbClient

class DeviceCommunication:
    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)

    def list_devices(self):
        return self.client.devices()
