import os
import sys
import json
import shutil

from utils import Utils
from modules import packages

class Analyzer:
    def __init__(self, folder):
        self.folder = folder
        self.dumps = Utils.list_files(folder, ".tar.gz")
        self.internal_path = None
        self.external_path = None
        self.app_id = self.app_id_parser()
        
        self.cache_path = os.path.join(sys.path[0], "cache")
        self.report_path = os.path.join(sys.path[0], "report")
        try:
            Utils.remove_folder(self.cache_path)
        except:
            pass
        Utils.check_and_generate_folder(self.cache_path)

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
        module_file = packages.get(self.app_id)
        if not module_file:
            print("[Analyzer] Module not found for {}".format(self.app_id))
            return None

        #tiktok   
        m = __import__("modules.{}".format(module_file), fromlist=[None])
        module = m.Module(self.internal_path, self.external_path)
        user_id = module.get_user_id()
        report_header = {
            "report_date": Utils.get_current_time(),
            "user": user_id
        }
        report = {}

        report["header"] = report_header
        report["profile"] = module.get_user_profile()
        report["messages"] = module.get_user_messages()
        report["users"] = module.get_user_profiles()
        report["searches"] = module.get_user_searches()
        report["videos"] = module.get_videos()
        report["freespace"] = module.get_undark_db()
        # with open("report/"+ name+"_freespace.txt",'w') as f:
        #         output = Utils.run_undark("./cache/tiktok/internal/databases/" + name)            
        #         print(output)
        f = open(os.path.join(self.report_path, "REPORT_{}.json".format(user_id)), "w")
        f.write(json.dumps(report, indent=2))
        f.close()
        # print(module.get_user_profiles())
        # print(module.get_user_id())
        # print(module.get_user_searches())
        # print(module.get_user_profile())
        # print(module.get_user_messages())