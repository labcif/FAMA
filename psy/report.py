import inspect
import os
import json
import logging
import time

from package.utils import Utils
from package.analyzer import Analyzer
from psy.psyutils import PsyUtils

from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.report.ReportProgressPanel import ReportStatus

class ReportOutput:
    def generateReport(self, baseReportDir, progressBar):
        logging.info("Starting Report Module")
        progressBar.setIndeterminate(True)

        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

        progressBar.updateStatusLabel("Finding source data")

        self.tempDirectory = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "FAMA")

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

        #Android Analyzer Smart Report
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

        #Classic Report
        if len(reports["reports"]) == 0:
            report = {}
            report["header"] = {
                "report_name": "Generated Report",
                "report_date": int(time.time()) * 1000,
                "app_name": "Generic",
                "app_id": "Generated Report"
            }

            has_row = False

            for artifact in PsyUtils.get_artifacts_list(): ##GGOODD
                artifact_name = artifact.getDisplayName()
                report[artifact_name] = []

                command = "WHERE (blackboard_artifacts.artifact_type_id = '{}')".format(artifact.getTypeID())
                rows = Case.getCurrentCase().getSleuthkitCase().getMatchingArtifacts(command)
                for row in rows:
                    has_row = True

                    item = {}
                    atts = row.getAttributes()
                    for att in atts:
                        item[att.getAttributeTypeDisplayName()] = str(att.getDisplayString().encode('utf-8','ignore'))

                    report[artifact_name].append(item)

            if not has_row:
                progressBar.complete(ReportStatus.ERROR)
                progressBar.updateStatusLabel("Nothing to report!")
                return

            report_path = os.path.join(baseReportDir, report["header"]["app_id"], "Generic")
            reporthtml = Analyzer.generate_html_report(report, report_path)
            Case.getCurrentCase().addReport(reporthtml, "Report", "Forensics Report")
            reports["reports"].append(Analyzer.generate_report_summary(report, "Generic"))

        report_file_path = Analyzer.generate_html_index(reports, baseReportDir)

        Case.getCurrentCase().addReport(report_file_path, "Report", "Forensics Report")

        progressBar.updateStatusLabel("Done")

        progressBar.complete(ReportStatus.COMPLETE)