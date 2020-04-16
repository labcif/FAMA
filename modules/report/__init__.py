import os
from package.utils import Utils

class ModuleParent:
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        # self.report_name = report_name
        self.internal_path = internal_path
        self.external_path = external_path
        
        # self.report_path = os.path.join(report_path, "report", self.report_name)
        self.report_path = report_path
        Utils.check_and_generate_folder(self.report_path)

        self.internal_cache_path = os.path.join(self.report_path, "Contents", "internal")
        self.external_cache_path = os.path.join(self.report_path, "Contents", "external")
        Utils.check_and_generate_folder(self.internal_cache_path)
        Utils.check_and_generate_folder(self.external_cache_path)

        if self.internal_path:
            Utils.extract_tar(self.internal_path, self.internal_cache_path)

        if self.external_path:
            Utils.extract_tar(self.external_path, self.external_cache_path)

        self.databases = self.set_databases()
        self.shared_preferences = self.set_shared_preferences() #we can comment this
        #print(self.databases)
        #print(self.shared_preferences)
        
        self.report = {}
        self.app_name = app_name
        self.app_id = app_id
        self.set_header()

    def set_databases(self):
        dbs = []
        dbs.extend(Utils.list_files(self.internal_cache_path, [".db"]))
        dbs.extend(Utils.list_files(self.external_cache_path, [".db"]))
        return dbs

    def set_shared_preferences(self):
        files = []
        for xmlfile in Utils.list_files(self.internal_cache_path, [".xml"]):
            if '/shared_prefs/' in xmlfile or '\\shared_prefs\\' in xmlfile:
                files.append(xmlfile)
        
        return files
    
    def set_header(self):
        self.report = {}
        report_header = {
            "report_name": Utils.get_current_time(),
            "report_date": Utils.get_current_millis(),
            "app_name" : self.app_name,
            "app_id": self.app_id
        }
        self.report["header"] = report_header

    def generate_report(self):
        raise NotImplementedError