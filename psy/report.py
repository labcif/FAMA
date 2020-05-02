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

        reports = []

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

                        info_report = {}
                        info_report["report_name"] = report_content["header"]["report_name"]
                        info_report["report_date"] = report_content["header"]["report_date"]
                        info_report["app_name"] = report_content["header"]["app_name"]
                        info_report["app_id"] = report_content["header"]["app_id"]
                        info_report["artifacts"] = len(report_content.keys()) - 1 #ignore header
                        info_report["link"] = "{}/{}/{}/report.html".format(fileset, app_id, app_report)
                        reports.append(info_report)

        if len(reports) == 0:
            progressBar.complete(ReportStatus.ERROR)
            progressBar.updateStatusLabel("Nothing to report!")
            return

        logging.info("Generating HTML index report")

        Utils.copy_tree(os.path.join(Utils.get_base_path_folder(), "template"), baseReportDir)
        try:
            os.remove(os.path.join(baseReportDir, "report.html")) #remove report.html from index
        except:
            pass

        report_file_path = os.path.join(baseReportDir, "index.html")
        Case.getCurrentCase().addReport(report_file_path, "Report", "Forensics Report")

        js_code = "var reportList = " + json.dumps(reports, indent = 2)

        handler = open(os.path.join(baseReportDir, "ListOfReports.js"), "w")
        handler.write(js_code)
        handler.close()

        progressBar.updateStatusLabel("Done")

        progressBar.complete(ReportStatus.COMPLETE)