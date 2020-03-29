from java.util.logging import Level

from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

from psy.ingest import ProjectIngestModule
from psy.settings import ProjectSettingsPanel
from psy.settings import ProjectSettingsPanelSettings

class ProjectIngestModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "TikTok"

    def __init__(self):
        self.settings = None
    
    #Module Settings
    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Forensics Analyzer"
        
    def getModuleVersionNumber(self):
        return "1.0"
    
    #Data Source Ingest
    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return ProjectIngestModule(self.settings)
  
    #Settings
    def getDefaultIngestJobSettings(self):
        return ProjectSettingsPanelSettings()
    
    def hasIngestJobSettingsPanel(self):
        return True

    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, ProjectSettingsPanelSettings):
            settings = ProjectSettingsPanelSettings()
        
        self.settings = settings
        return ProjectSettingsPanel(self.settings)