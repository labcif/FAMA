import os
import json
from package.utils import Utils
from package.logsystem import LogSystem

from distutils.dir_util import copy_tree

class Analyzer:
    def __init__(self, app, folder, report_folder):
        self.log = LogSystem("analyser")
        self.folder = folder
        if '.' in app:
            self.app = Utils.find_app_name(app)
            self.app_id = app
        else:
            self.app = app
            self.app_id = Utils.find_package(app)

        self.dumps = Utils.list_files(folder, ".tar.gz")
        self.internal_path = None
        self.external_path = None
        
        self.report_path = os.path.join(report_folder, "report")
        Utils.check_and_generate_folder(self.report_path)
        
        self.initialize_dumps()
    
    def initialize_dumps(self):
        for name in self.dumps:
            if '_internal.tar.gz' in name:
                self.internal_path = name
            elif '_external.tar.gz' in name:
                self.external_path = name

    def generate_report(self):
        if not self.app_id:
            self.log.critical("Module not found for application {}".format(self.app))
            return None

        if not self.app:
            self.log.critical("Module not found for {} package".format(self.app_id))
            return None

        if not self.internal_path:
            self.log.critical("No data file found for {} package".format(self.app_id))
            return None

        self.log.info("Module {} for {}".format(self.app, self.app_id))

        m = __import__("modules.report.{}".format(self.app), fromlist=[None])
        module = m.ModuleReport(self.internal_path, self.external_path, self.report_path, self.app, self.app_id)
        
        # Utils.remove_folder(os.path.join(self.report_path))
        
        return {"Report_1": module.generate_report()}

    @staticmethod
    def generate_html_report(reports, output_folder, add_folder = True):
        report_path = output_folder
        
        if add_folder:
            report_path = os.path.join(output_folder, "report")
            Utils.check_and_generate_folder(report_path)
            
        log = LogSystem("analyser")
        log.info("Generating HTML report")

        copy_tree(os.path.join(Utils.get_base_path_folder(), "template"), report_path)

        report_file_path = os.path.join(report_path, "index.html")
        
        js_code = "var reportData = " + json.dumps(reports, indent = 2)

        handler = open(os.path.join(report_path, "Report.js"), "w")
        handler.write(js_code)
        handler.close()

        return report_file_path
        

        

