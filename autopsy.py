import os
import sys
import logging

sys.path.append(os.path.dirname(__file__)) #include this path to module autopsy

from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.report import GeneralReportModuleAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.corecomponentinterfaces import DataSourceProcessor  
from org.sleuthkit.autopsy.casemodule import Case

from psy.ingest import ProjectIngestModule
from psy.report import ReportOutput
from psy.settings import ProjectIngestSettingsPanel, ProjectReportSettingsPanel, DataSourcesPanelSettings
    
class ProjectIngestModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "LabCif - Android Forensics"

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
    moduleName = "LabCif - Android Forensics Report"

    def __init__(self):
        self.settings = None
        self.report = ReportOutput()

    def getName(self):
        return self.moduleName

    def getDescription(self):
        return "Android Forensics Framework Report Generator"

    def generateReport(self, baseReportDir, progressBar):
        self.report.generateReport(baseReportDir, progressBar)
    
    def getConfigurationPanel(self):
        self.configPanel = ProjectReportSettingsPanel()
        return self.configPanel

    def getRelativeFilePath(self):
        return "index.html"

class ProjectDSProcessor(DataSourceProcessor):
    configPanel = None

    def __init__(self):
        self.configPanel = DataSourcesPanelSettings()
    
    @staticmethod
    def getType():
        return "Live extraction with ADB (Android)"

    def getDataSourceType(self):
        return "Live extraction with ADB (Android)"

    def getPanel(self):
        return self.configPanel

    def isPanelValid(self):
        return self.configPanel.validatePanel()

    def run(self, progressMonitor, callback):
        pass
        #self.jp.storeSettings()
        #run(UUID.randomUUID().toString(), configPanel.getImageFilePath(), configPanel.getProfile(), configPanel.getPluginsToRun(), configPanel.getTimeZone(), progressMonitor, callback);

    def cancel(self):
        logging.info("cancel")
        pass
        #if (addImageTask != null) {
        #    addImageTask.cancelTask();
        #}

    def reset(self):
        #self.configPanel.reset()
        logging.info("reset")
        #configPanel.reset()
        pass
