import inspect
import os
import json
import logging

from package.utils import Utils
from package.analyzer import Analyzer

from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.report.ReportProgressPanel import ReportStatus

class ReportOutput:
    def generateReport(self, baseReportDir, progressBar):
        logging.info("Starting Report Module")
        progressBar.setIndeterminate(True)

        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

        self.reports = {}

        progressBar.updateStatusLabel("Finding source data")

        self.tempDirectory = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics")

        if not os.path.exists(self.tempDirectory):
            progressBar.complete(ReportStatus.ERROR)
            progressBar.updateStatusLabel("Run Ingest Module first!")
            return

        for app_directory in os.listdir(self.tempDirectory):
            for app_report in os.listdir(os.path.join(self.tempDirectory, app_directory)):
                report = os.path.join(self.tempDirectory, app_directory, app_report, "report", "Report.json")
                logging.info(str(report))
                if os.path.exists(report):
                    self.reports["Report_{}".format(app_report)] = Utils.read_json(report)

        progressBar.updateStatusLabel("Creating report")

        report_path = Analyzer.generate_html_report(self.reports, baseReportDir)

        Case.getCurrentCase().addReport(report_path, "Report", "Forensics Report")

        progressBar.updateStatusLabel("Done")

        progressBar.complete(ReportStatus.COMPLETE)