import inspect

from java.util import UUID
from java.util.logging import Level
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.datamodel import BlackboardAttribute

from psy.progress import ProgressUpdater

class PsyUtils:
    def __init__(self):
        self._logger = Logger.getLogger("Ingest Logger")
        self.moduleName = "TIKTOK - TEST - "

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    @staticmethod
    def generate_new_fileset(name, folder):
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

    def create_attribute_type(self, att_name, type, att_desc, skCase):
        try:
            skCase.addArtifactAttributeType(att_name, type, att_desc)
        except:
            self.log(Level.INFO, " Error creating attribute type: " + att_desc)
        return skCase.getAttributeType(att_name)
    
    def create_artifact_type(self, art_name, art_desc, skCase):
        try:
            skCase.addBlackboardArtifactType(art_name, self.moduleName + art_desc)
        except:
            self.log(Level.INFO, self.moduleName +" Error creating artifact type: " + art_desc)
        art = skCase.getArtifactType(art_name)
        return art
    
    @staticmethod
    def index_artifact(blackboard, artifact, artifact_type):
        try:
            # Index the artifact for keyword search
            blackboard.indexArtifact(artifact)
        except Blackboard.BlackboardException as e:
            pass
            #self.log(Level.INFO, self.moduleName + " Error indexing artifact " + artifact.getDisplayName() + "" +str(e))
        # Fire an event to notify the UI and others that there is a new log artifact
        IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent("test",artifact_type, None))

    @staticmethod
    def blackboard_attribute(attribute):
        return {
            "byte": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE,
            "datetime": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME,
            "double": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DOUBLE,
            "integer": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.INTEGER,
            "long": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG,
            "string": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING
        }.get(attribute)
        