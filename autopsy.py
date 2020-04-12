from java.util.logging import Level

from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.report import GeneralReportModuleAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter

from psy.ingest import ProjectIngestModule
from psy.report import ReportOutput
from psy.settings import ProjectIngestSettingsPanel
from psy.settings import ProjectReportSettingsPanel


class ProjectIngestModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "TikTok (to be changed)"

    def __init__(self):
        self.settings = None
    
    #Module Settings
    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Android forensics framework. Extract, analyze and generate reports based on user data."
        
    def getModuleVersionNumber(self):
        return "1.0"
    
    #Data Source Ingest
    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return ProjectIngestModule(self.settings)
  
    #Settings
    def getDefaultIngestJobSettings(self):
        return GenericIngestModuleJobSettings()
    
    def hasIngestJobSettingsPanel(self):
        return True

    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, GenericIngestModuleJobSettings):
            raise IllegalArgumentException("Expected settings argument to be instanceof GenericIngestModuleJobSettings")
        
        self.settings = settings
        return ProjectIngestSettingsPanel(self.settings)

class ProjectIngestModuleReport(GeneralReportModuleAdapter):
    moduleName = "Unnamed Project Report"

    def __init__(self):
        self.settings = None
        self.report = ReportOutput()

    def getName(self):
        return self.moduleName

    def getDescription(self):
        return "Android Forensics Framework Report Generator"

    def generateReport(self, baseReportDir, progressBar):
        self.generateReport(baseReportDir, progressBar)
    
    def getConfigurationPanel(self):
        self.configPanel = ProjectReportSettingsPanel()
        return self.configPanel