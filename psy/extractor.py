from package.extract import Extract

class Extractor:
    def __init__(self, apps, devices, progress, dsprocessor = True):
        self.apps = apps
        self.progress = progress
        self.devices = devices
        #Extract instance, the dump folder is going to be the same for all apps dumps
        self.extract = Extract()
        self.dsprocessor = dsprocessor

    def dump_apps(self):
        folders = {}
        # For each extract of the app with device context
        for app_id in self.apps:
            #Extract from datasource processor     
            if self.dsprocessor:
                self.progress.setProgressText('  Extracting application data ({}).\n  Please wait.'.format(app_id))
            else:
                self.progress.progress('Extracting application data ({})'.format(app_id))
            
            for serial, folder in self.extract.dump_from_adb(app_id, devices = self.devices).items():
                # If the device not in the list
                if not folders.get(serial):
                    folders[serial] = []

                # If the folder is not the list for the device, add it
                if not folder in folders[serial]:
                    folders[serial].append(folder)

                #self.progressJob.next_job("Extracting {}".format(app_id))
        return folders
        