import inspect

from java.util.logging import Level
from org.sleuthkit.autopsy.coreutils import Logger

class PsyUtils:
    def __init__(self):
        self._logger = Logger.getLogger("Ingest Logger")

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def generate_new_fileset(self, name, folder):
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        skcase_data = Case.getCurrentCase()
        device_id = UUID.randomUUID() #use real adb device in future?
        skcase_data.notifyAddingDataSource(device_id)
        progress_updater = ProgressUpdater() 
        
        newDataSources = []
        newDataSource = fileManager.addLocalFilesDataSource(str(device_id), name, "", folder, progress_updater)
        newDataSources.append(newDataSource.getRootDirectory())
        
        files_added = progress_updater.getFiles()
        
        for file_added in files_added:
            skcase_data.notifyDataSourceAdded(file_added, device_id)
