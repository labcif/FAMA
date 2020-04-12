import sys
import json
import os
import tarfile

from utils import Utils
from modules.report import ModuleParent

if sys.executable and "python" in sys.executable.lower():
    from database import Database
else: #jython #improve relative imports!!
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from database import Database

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)
        print("[Tiktok] Module started")
    
    def generate_report(self):

        self.report["profile"] = self.get_user_profile()
        self.report["messages"] = self.get_user_messages()
        self.report["users"] = self.get_user_profiles()
        self.report["searches"] = self.get_user_searches()
        self.report["videos"] = self.get_videos()
        self.report["published_videos"] = self.get_videos_publish()
        self.report["freespace"] = self.get_undark_db()
        self.report["log"] = self.get_last_session()

        print("[Tiktok] Generate Report")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

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
        results = database.execute_query("select UID, UNIQUE_ID, NICK_NAME, datetime(created_time/1000, 'unixepoch', 'localtime') as created_time, content as message, case when read_status = 0 then 'Not read' when read_status = 1 then 'Read' else read_status end read_not_read, local_info, type, case when deleted = 0 then 'Not deleted' when read_status = 1 then 'Deleted' else deleted end from SIMPLE_USER, msg where UID = sender order by created_time;", attach = attach)
        
        for entry in results:
            message={}
            message["uid"] = entry[0]
            message["uniqueid"] = entry[1]
            message["nickname"] = entry[2]
            message["createdtime"] = entry[3]
            message["readstatus"] = entry[5]
            message["localinfo"] = entry[6]
            message_type = entry[7]

            message_dump = json.loads(entry[4])
            body=""

            if  message_type == 7: #text message type
                message["type"] = "text"
                body = message_dump.get("text")

            elif message_type == 8: #video message type
                message["type"] = "video"
                body= "https://www.tiktok.com/@tiktok/video/{}".format(message_dump.get("itemId"))
            
            elif message_type == 5:
                message["type"] = "gif"
                body=message_dump.get("url").get("url_list")[0]
            else:
                body= str(message_dump)
            
            message["message"] = body

            message["deleted"] = entry[8]
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
            
        user_profile["url"] = "https://www.tiktok.com/@{}".format(user_profile["unique_id"])
                #except ValueError:
                #    print("[Tiktok] JSON User Error")

        return user_profile

    def get_user_searches(self):
        print("[Tiktok] Getting User Search History...")
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "search.xml")
        searches = []
        #verify if recent hisotry tag exists
        try:
            dump = json.loads(Utils.xml_attribute_finder(xml_file, "recent_history")["recent_history"])
            for i in dump: searches.append(i["keyword"])
        except:
            pass
        
        

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
            message["url"] = "https://www.tiktok.com/@{}".format(message["uniqueid"])
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

        print("[Tiktok] {} video(s) found".format(len(videos)))
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
    

    def get_videos_publish(self):
        print("[Tiktok] Getting published videos")
        videos = []
        base_path = os.path.join(self.internal_cache_path, "cache", "aweme_publish")
        aweme_publish_files = os.listdir(base_path)

        for aweme_file in aweme_publish_files:
            dump = Utils.read_json(os.path.join(base_path, aweme_file))
            aweme_list = dump.get("aweme_list")
            
            for entry in aweme_list:
                video ={}
                video["created_time"] = entry.get("create_time")
                video["video"] = entry.get("video").get("animated_cover").get("url_list")[0]
                videos.append(video)
    
        print("[Tiktok] {} video(s) found".format(len(videos)))
        return videos


    
    def get_last_session(self):
        print("[Tiktok] Getting last session...")
        session = []

        relevant_keys = ["page", "request_method", "is_first","duration","is_first","rip","duration","author_id","access2","video_duration","video_quality","access",
        "page_uid","previous_page","enter_method","enter_page","key_word","search_keyword","next_tab","search_type", "play_duration", "content"]

        db = os.path.join(self.internal_cache_path, "databases", "ss_app_log.db")
        database = Database(db)
        database.execute_pragma()
        results = database.execute_query("select tag, ext_json, datetime(timestamp/1000, 'unixepoch', 'localtime'), session_id from event order by timestamp")
        
        for entry in results:
            session_entry={}
            session_entry["action"] = entry[0]
            
            body_dump = json.loads(entry[1])
            session_entry["time"] = entry[2]
            session_entry["session_id"] = entry[3]
            session.append(session_entry)

            #json body parser
            body = {}
            for key, value in body_dump.items():     
                if key in relevant_keys:
                    body[key] = value
            
            session_entry["body"] =body

        print("[Tiktok] {} entrys found".format(len(results)))
        return session

