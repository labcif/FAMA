import os
import sys
import logging

# sys.path.append(os.path.dirname(__file__)) #include this path to module autopsy

from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.report import GeneralReportModuleAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.datasourceprocessors import DataSourceProcessorAdapter  
from org.sleuthkit.autopsy.casemodule import Case

from psy.ingest import ProjectIngestModule
from psy.report import ReportOutput
from psy.processor import DataSourcesPanelSettings
from psy.settings import ProjectIngestSettingsPanel, ProjectReportSettingsPanel
from psy.psyutils import PsyUtils

VERSION = "1.1"
    
#3 Modules - Ingest, Report, DatasourceProcessor
class ProjectIngestModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "LabCif - FAMA"

    def __init__(self):
        self.settings = None
    
    #Module Settings
    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "FAMA framework. Extract, analyze and generate reports based on user data."
        
    def getModuleVersionNumber(self):
        return VERSION
    
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
    moduleName = "LabCif - FAMA Report"

    def __init__(self):
        self.settings = None
        self.report = ReportOutput()

    def getName(self):
        return self.moduleName

    def getDescription(self):
        return "Forensic Analysis for Mobile Apps Framework Report Generator"

    def generateReport(self, settings, progressBar):
        autopsy_version = PsyUtils.get_autopsy_version()
        baseReportDir = settings
        if (autopsy_version["major"] == 4 and autopsy_version["minor"] >= 16):
            baseReportDir = settings.getReportDirectoryPath()
        
        self.report.generateReport(baseReportDir, progressBar)

    def getConfigurationPanel(self):
        self.configPanel = ProjectReportSettingsPanel()
        return self.configPanel

    def getRelativeFilePath(self):
        return "index.html"

class ProjectDSProcessor(DataSourceProcessorAdapter):
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

    def run(self, host, progressMonitor, callback):
        self.configPanel.run(host, progressMonitor, callback)
