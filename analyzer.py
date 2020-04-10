import os
from utils import Utils

class Analyzer:
    def __init__(self, app, folder, report_folder):
        self.folder = folder
        self.app = app
        self.app_id = Utils.find_package(self.app)
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
            print("[Analyzer] Module not found for {}".format(self.app))
            return None

        print("[Analyzer] Module {} for {}".format(self.app, self.app_id))

        m = __import__("modules.report.{}".format(self.app), fromlist=[None])
        module = m.ModuleReport(self.internal_path, self.external_path, self.report_path)

        module.generate_report()