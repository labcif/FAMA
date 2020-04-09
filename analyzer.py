import os
import sys
import json
import shutil
import tarfile


from utils import Utils
from modules import packages

class Analyzer:
    def __init__(self, folder, report_folder):
        self.folder = folder
        self.dumps = Utils.list_files(folder, ".tar.gz")
        self.internal_path = None
        self.external_path = None
        self.app_id = self.app_id_parser()
        
        self.report_path = os.path.join(report_folder, "report")
        
        Utils.check_and_generate_folder(self.report_path)

    def app_id_parser(self):
        app_id = None
        for name in self.dumps:
            if '_internal.tar.gz' in name:
                self.internal_path = name
                app_id = os.path.basename(name.split('_internal.tar.gz')[0])
            elif '_external.tar.gz' in name:
                self.external_path = name
                app_id = os.path.basename(name.split('_external.tar.gz')[0])
        
        return app_id

    def generate_report(self):
        # report_name = "Report_{}".format(Utils.get_current_time())
        module_file = packages.get(self.app_id)

        if not module_file:
            print("[Analyzer] Module not found for {}".format(self.app_id))
            return None

        m = __import__("modules.{}".format(module_file), fromlist=[None])
        module = m.ModuleReport(self.internal_path, self.external_path, self.report_path)

        module.generate_report()