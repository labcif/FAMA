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

        progressBar.updateStatusLabel("Finding source data")

        self.tempDirectory = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics")

        if not os.path.exists(self.tempDirectory):
            progressBar.complete(ReportStatus.ERROR)
            progressBar.updateStatusLabel("Run Ingest Module first!")
            return

        progressBar.updateStatusLabel("Creating report")

        
        os.environ["CASE_NAME"] = Case.getCurrentCase().getName()
        os.environ["CASE_NUMBER"] = Case.getCurrentCase().getNumber()
        os.environ["EXAMINER"] = Case.getCurrentCase().getExaminer()

        reports = {}
        reports["reports"] = []

        for fileset in os.listdir(self.tempDirectory):
            fileset_path = os.path.join(self.tempDirectory, fileset)
            for app_id in os.listdir(fileset_path):
                app_path = os.path.join(fileset_path, app_id)
                for app_report in os.listdir(app_path):
                    report = os.path.join(app_path, app_report, "Report.json")
                    if os.path.exists(report):
                        report_content = Utils.read_json(report)

                        report_path = Analyzer.generate_html_report(report_content, os.path.join(app_path, app_report))
                        
                        Case.getCurrentCase().addReport(report_path, "Report", "Forensics Report")

                        reports["reports"].append(Analyzer.generate_report_summary(report_content, app_report, fileset = fileset))

        if len(reports) == 0:
            progressBar.complete(ReportStatus.ERROR)
            progressBar.updateStatusLabel("Nothing to report!")
            return
        
        report_file_path = Analyzer.generate_html_index(reports, baseReportDir)

        Case.getCurrentCase().addReport(report_file_path, "Report", "Forensics Report")

        progressBar.updateStatusLabel("Done")

        progressBar.complete(ReportStatus.COMPLETE)