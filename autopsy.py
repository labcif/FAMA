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
from psy.processor import DataSourcesPanelSettings
from psy.settings import ProjectIngestSettingsPanel, ProjectReportSettingsPanel
    
#3 Modules - Ingest, Report, DatasourceProcessor
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
    moduleName = "Live extraction with ADB (Android)"

    def __init__(self):
        self.configPanel = DataSourcesPanelSettings()
    
    @staticmethod
    def getType():
        return ProjectDSProcessor.moduleName

    def getDataSourceType(self):
        return self.moduleName

    def getPanel(self):
        return self.configPanel

    def isPanelValid(self):
        return self.configPanel.validatePanel()

    def run(self, progressMonitor, callback):
        self.configPanel.run(progressMonitor, callback)

    def cancel(self):
        logging.info("cancel") #implement? #cancel thread

    def reset(self):
        pass
