import sys
import json
import os
import tarfile
# import time
# import datetime

if sys.executable and "python" in sys.executable.lower():
    from database import Database
else: #jython
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from database import Database

from modules import ModuleParent
from utils import Utils

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path):
        ModuleParent.__init__(self, internal_path, external_path, report_path)
        print("[Tiktok] Module started")

    def generate_report(self):
        user_id = self.get_user_id()
        report_header = {
            "report_date": Utils.get_current_time(),
            "user": user_id
        }
        report = {}
        report["header"] = report_header
        report["profile"] = self.get_user_profile()
        report["messages"] = self.get_user_messages()
        report["users"] = self.get_user_profiles()
        report["searches"] = self.get_user_searches()
        report["videos"] = self.get_videos()
        report["freespace"] = self.get_undark_db() 
        print("[Tiktok] Generate Report")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), report)
        return report

    #TIKTOK
    def get_user_messages(self):
        print("[Tiktok] Getting User Messages...")
        messages_list = []

        db1 = os.path.join(self.internal_cache_path, "databases", "db_im_xx")
        db2 = None

        for db in self.databases:
            if db.endswith("_im.db"):
                db2 = db
                break
        
        if not db2:
            print("[Tiktok] User Messages database not found!")
            return ""

        db2 = os.path.join(self.internal_path, db2)
        attach = "ATTACH '{}' AS 'db2'".format(db2)

        database = Database(db1)
        results = database.execute_query("select UID, UNIQUE_ID, NICK_NAME, datetime(created_time/1000, 'unixepoch', 'localtime') as created_time, content as message, case when read_status = 0 then 'Not read' when read_status = 1 then 'Read' else read_status end read_not_read, local_info from SIMPLE_USER, msg where UID = sender order by created_time;", attach = attach)
        for entry in results:
            message={}
            message["uid"] = entry[0]
            message["uniqueid"] = entry[1]
            message["nickname"] = entry[2]
            message["createdtime"] = entry[3]
            message["message"] = entry[4]
            message["readstatus"] = entry[5]
            message["localinfo"] = entry[6]
            messages_list.append(message)
        
        print("[Tiktok] {} messages found".format(len(messages_list)))

        if not db1 in self.used_databases:
            self.used_databases.append(db1)
        
        if not db2 in self.used_databases:
            self.used_databases.append(db2)

        return messages_list

    def get_user_profile(self):
        print("[Tiktok] Get User Profile...")
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "aweme_user.xml")
        user_profile ={}
        values = Utils.xml_attribute_finder(xml_file)
        for key, value in values.items():
            if key.endswith("_aweme_user_info"):
                #try:
                dump=json.loads(value)
                atributes =["account_region", "follower_count","following_count", "gender", "google_account", "is_blocked", "is_minor", "nickname", "register_time", "sec_uid", "short_id", "uid", "unique_id"]

                for index in atributes:
                    user_profile[index] = dump[index]
                break
                #except ValueError:
                #    print("[Tiktok] JSON User Error")

        return user_profile

    def get_user_searches(self):
        print("[Tiktok] Getting User Search History...")
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "search.xml")
        dump = json.loads(Utils.xml_attribute_finder(xml_file, "recent_history")["recent_history"])
        searches = []
        for i in dump: searches.append(i["keyword"])

        print("[Tiktok] {} search entrys found".format(len(searches)))
        return searches

    def get_user_profiles(self):
        print("[Tiktok] Getting User Profiles...")
        profiles = []

        db = os.path.join(self.internal_cache_path, "databases", "db_im_xx")

        database = Database(db)
        results = database.execute_query("select UID, UNIQUE_ID, NICK_NAME, AVATAR_THUMB, case when follow_status = 1 then 'Following' when follow_status = 2 then 'Followed and Following ' else 'Invalid' end from SIMPLE_USER")
        for entry in results:
            message={}
            message["uid"] = entry[0]
            message["uniqueid"] = entry[1]
            message["nickname"] = entry[2]
            dump_avatar = json.loads(entry[3])
            message["avatar"] = dump_avatar["url_list"][0]
            message["follow_status"] = entry[4]
            profiles.append(message)
        
        print("[Tiktok] {} profiles found".format(len(profiles)))

        if not db in self.used_databases:
            self.used_databases.append(db)

        return profiles

    def get_user_id(self):
        print("[Tiktok] Getting User ID")
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "iuserstate.xml")
        return Utils.xml_attribute_finder(xml_file, "userid")["userid"]

    def get_videos(self):
        print("[Tiktok] Getting Videos...")
        videos = []
        db = os.path.join(self.internal_cache_path, "databases", "video.db")

        database = Database(db)
        results = database.execute_query("select key, extra from video_http_header_t")

        for entry in results:
            video = {}
            video["key"] = entry[0]
            dump = json.loads(entry[1])
            
            for line in dump["responseHeaders"].splitlines():
                if 'Last-Modified:' in line:
                    video["last_modified"] = line.split(": ")[1]
                    break
            videos.append(video)
            #self.access_path_file(self.internal_path, "./cache/cache/{}".format(entry[0]))
        
        if not db in self.used_databases:
            self.used_databases.append(db)

        print("[Tiktok] {} videos found".format(len(videos)))
        return videos
    
    def get_undark_db(self):
        print("[Tiktok] Getting undark output...")
        output = {}

        for name in self.used_databases:
            listing = []
            undark_output = Utils.run_undark(name).decode()
            for line in undark_output.splitlines():
                listing.append(line)
            
            if listing:
                relative_name = os.path.normpath(name.replace(self.report_path, "")) #clean complete path
                output[relative_name] = listing

        return output

class ModulePsy:
    def __init__(self, case):
        self.case = case
        
        #self.process_messages(messages, file)
        #self.process_user_profile(user_profile, file)
        #self.process_users(profiles, file)
        #self.process_searches(searches, file)
        #self.process_undark(unkdark_ouput, file)
        #self.process_videos(videos, report_number, file)
        #self.att_msg_uid = self.utils.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", skCase)
        #self.art_messages = self.utils.create_artifact_type("TIKTOK_MESSAGES","MESSAGES", skCase)
