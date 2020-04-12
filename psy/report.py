import inspect
import os
import json

from distutils.dir_util import copy_tree

from utils import Utils

from java.util.logging import Level
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.report.ReportProgressPanel import ReportStatus

class ReportOutput:
    def __init__(self):
        self._logger = Logger.getLogger("ProjectIngestReport")

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)
    
    def generateReport(self, baseReportDir, progressBar):
        self.log(Level.INFO, "Starting Report Module")
        progressBar.setIndeterminate(True)

        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

        self.reports = {}

        progressBar.updateStatusLabel("Finding source data")

        self.tempDirectory = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics")

        for app_directory in os.listdir(self.tempDirectory):
            for app_report in os.listdir(os.path.join(self.tempDirectory, app_directory)):
                report = os.path.join(self.tempDirectory, app_directory, app_report, "report", "Report.json")
                self.log(Level.INFO, str(report))
                if os.path.exists(report):
                    self.reports["Report_{}".format(app_report)] = Utils.read_json(report)

        progressBar.updateStatusLabel("Creating report")

        copy_tree(os.path.join(Utils.get_base_path_folder(), "template"), baseReportDir)

        report_path = os.path.join(baseReportDir, "index.html")
        
        js_code = "var reportData = " + json.dumps(self.reports, indent = 2)

        handler = open(os.path.join(baseReportDir, "Report.js"), "w")
        handler.write(js_code)
        handler.close()

        Case.getCurrentCase().addReport(report_path, "Report", "Forensics Report")

        progressBar.updateStatusLabel("Done")

        progressBar.complete(ReportStatus.COMPLETE)