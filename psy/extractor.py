import os

from package.extract import Extract
from package.utils import Utils

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
                self.progress.next_job('Extracting application data ({})'.format(app_id))

            for serial, folder in self.extract.dump_from_adb(app_id, devices = self.devices).items():
                # If the device not in the list
                if not folders.get(serial):
                    folders[serial] = []

                # If the folder is not the list for the device, add it
                if not folder in folders[serial]:
                    folders[serial].append(folder)


        for serial, folderslist in folders.items():
            extracted_list = []

            for folder in folderslist:
                extracted_list.append(self.extract_dumps(serial, folder))

            folders[serial] = extracted_list

        return folders

    def extract_dumps(self, serial, folder):
        files = os.listdir(folder)

        self.internal_path = os.path.join(folder, "data", "data")
        self.external_path = os.path.join(folder, "data", "media", "0", "Android", "data")

        Utils.check_and_generate_folder(self.internal_path)
        Utils.check_and_generate_folder(self.external_path)

        if self.dsprocessor:
            self.progress.setProgressText('  Handling extracted data from {}.\n  Please wait.'.format(serial))
        else:
            self.progress.change_text('Handling extracted data from {}'.format(serial))

        for filename in files:
            if '_internal.tar.gz' in filename:
                Utils.extract_tar(os.path.join(folder, filename), os.path.join(self.internal_path, filename.replace('_internal.tar.gz', '')))
            elif '_external.tar.gz' in filename:
                Utils.extract_tar(os.path.join(folder, filename), os.path.join(self.external_path, filename.replace('_external.tar.gz', '')))

        return os.path.join(folder, "data")
