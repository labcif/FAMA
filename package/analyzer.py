import os
import json
import logging
from package.utils import Utils

class Analyzer:
    def __init__(self, app, folder, report_path):
        if '.' in app:
            self.app = Utils.find_app_name(app)
            self.app_id = app
        else:
            self.app = app
            self.app_id = Utils.find_package(app)

        self.internal_path = None
        self.external_path = None
        self.folder = folder
        
        self.report_path = report_path
        Utils.remove_folder(self.report_path)
        
        self.initialize_dumps()
    
    def initialize_dumps(self):
        for name in os.listdir(self.folder):
            if self.app_id + '_internal.tar.gz' in name:
                self.internal_path = os.path.join(self.folder, name)
            elif self.app_id +  '_external.tar.gz' in name:
                self.external_path = os.path.join(self.folder, name)

    def generate_report(self):
        if not self.app_id:
            logging.critical("Module not found for application {}".format(self.app))
            return None

        if not self.app:
            logging.critical("Module not found for {} package".format(self.app_id))
            return None

        logging.info("Found module {} for {}".format(self.app, self.app_id))

        logging.info("Looking for {} data in {}".format(self.app, self.folder))

        # self.report_path = os.path.join(report_path, "report", self.report_name)
        Utils.check_and_generate_folder(self.report_path)

        self.internal_cache_path = os.path.join(self.report_path, "Contents", "internal")
        self.external_cache_path = os.path.join(self.report_path, "Contents", "external")
        
        if self.internal_path or self.external_path:
            logging.info("Dump file found. Extracting dump.")
            if self.internal_path:
                Utils.extract_tar(self.internal_path, self.internal_cache_path)

            if self.external_path:
                Utils.extract_tar(self.external_path, self.external_cache_path)
        else:
            self.internal_path = os.path.join("data", "data", self.app_id)
            self.external_path = os.path.join("data", "media", "0", "Android", "data", self.app_id)

            int_find = Utils.find_folder_has_folder(self.internal_path, self.folder)
            if int_find:
                Utils.copy_tree(int_find, self.internal_cache_path)
            
            ext_find = Utils.find_folder_has_folder(self.external_path, self.folder)
            if ext_find:
                Utils.copy_tree(ext_find, self.external_cache_path)

            if not int_find and not ext_find:
                logging.info("Application data for {} not found".format(self.app))
                return None

        m = __import__("modules.report.{}".format(self.app), fromlist=[None])
        module = m.ModuleReport(self.internal_cache_path, self.external_cache_path, self.report_path, self.app, self.app_id)
        
        # Utils.remove_folder(os.path.join(self.report_path))
        
        return module.generate_report()

    @staticmethod
    def generate_html_report(reports, report_path):
        logging.info("Generating HTML report")

        Utils.check_and_generate_folder(report_path)

        Utils.copy_tree(os.path.join(Utils.get_base_path_folder(), "template"), report_path)

        report_file_path = os.path.join(report_path, "report.html")

        try:
            os.remove(os.path.join(report_path, "index.html")) #remove report.html from index
        except:
            pass
        
        if not reports.get("header"):
            reports["header"] = {}

        reports["header"]["case_name"] = os.environ.get("case_name".upper())
        reports["header"]["case_number"] = os.environ.get("case_number".upper())
        reports["header"]["examiner"] = os.environ.get("examiner".upper())
        
        js_code = "var reportData = " + json.dumps(reports, indent = 2)

        assets_folder = os.path.join(report_path, "assets")
        Utils.check_and_generate_folder(assets_folder)

        handler = open(os.path.join(assets_folder, "Report.js"), "w")
        handler.write(js_code)
        handler.close()

        return report_file_path

    @staticmethod
    def generate_report_summary(report, app_report, fileset = None):
        info_report = {}
        info_report["report_name"] = report["header"]["report_name"]
        info_report["report_date"] = report["header"]["report_date"]
        info_report["app_name"] = report["header"]["app_name"]
        info_report["app_id"] = report["header"]["app_id"]
        info_report["artifacts"] = len(report.keys()) - 1 #ignore header
        
        if fileset:
            info_report["link"] = "../../ModuleOutput/AndroidForensics/{}/{}/{}/report.html".format(fileset, info_report["app_id"], app_report)
        else:
            info_report["link"] = "{}/{}/report.html".format(info_report["app_id"], app_report)

        return info_report

    @staticmethod
    def generate_html_index(reports, report_path):
        logging.info("Generating HTML index report")
        
        Utils.copy_tree(os.path.join(Utils.get_base_path_folder(), "template"), report_path)
        try:
            os.remove(os.path.join(report_path, "report.html")) #remove report.html from index
        except:
            pass

        report_file_path = os.path.join(report_path, "index.html")

        reports["case_name"] = os.environ.get("case_name".upper())
        reports["case_number"] = os.environ.get("case_number".upper())
        reports["examiner"] = os.environ.get("examiner".upper())

        js_code = "var reportList = " + json.dumps(reports, indent = 2)

        assets_folder = os.path.join(report_path, "assets")
        Utils.check_and_generate_folder(assets_folder)

        handler = open(os.path.join(assets_folder, "ListOfReports.js"), "w")
        handler.write(js_code)
        handler.close()

        return report_file_path

        

