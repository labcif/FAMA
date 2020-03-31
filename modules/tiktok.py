import sys
import json
import os

#try:
#    import sqlite3
#except:
#    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#    from jythonsqlite3 import module as sqlite3
    
try:
    from database import Database
except: #jython fix
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from database import Database

from utils import Utils

class Module:
    def __init__(self, internal_path, external_path):
        print("[Tiktok] Module loaded")
        self.internal_path = internal_path
        self.external_path = external_path

        self.cache_path = os.path.join(Utils.get_base_path_folder(), "cache", "tiktok")
        Utils.check_and_generate_folder(self.cache_path)

        self.databases = self.set_databases()
        self.shared_preferences = self.set_shared_preferences()
        # self.videos = self.set_videos()

        #print(self.databases)
        #print(self.shared_preferences)

        print("[Tiktok] Module started")

    def set_databases(self):
        dbs = []
        dbs.extend(Utils.list_files_tar(self.internal_path, [".db"]))
        dbs.extend(Utils.list_files_tar(self.external_path, [".db"]))
        return dbs

    def set_shared_preferences(self):
        files = []
        for xmlfile in Utils.list_files_tar(self.internal_path, [".xml"]):
            if '/shared_prefs/' in xmlfile:
                files.append(xmlfile)
        
        return files
    # def set_videos(self):
    #     files = []
    #     print("entrou nos videos")
    #     for mp4 in Utils.list_files_tar(self.internal_path, [""]):
    #         if '/cache/cache/' in mp4:
    #             files.append(mp4)

    #     print("tamanho:{}".format(len(files)))
    #     return files

    def access_path_file(self, dump_path, file_path):
        if '_internal.tar.gz' in dump_path:
            middle = "internal"
        elif '_external.tar.gz' in dump_path:
            middle = "external"
        else:
            middle = ""

        cache_path = os.path.join(self.cache_path, middle, Utils.replace_slash_platform(file_path[2:])) #clean ./

        if os.path.exists(cache_path):
            return cache_path
        
        if not Utils.extract_file_tar(dump_path, file_path, cache_path):
            print("[Tiktok] Extract failed for {} with file {}".format(dump_path, file_path))
        
        return cache_path
        
    #TIKTOK
    def get_user_messages(self):
        print("[Tiktok] Getting User Messages...")
        messagesList =[]
        #sqlite3.SQLITE_ATTACH

        db1 = self.access_path_file(self.internal_path, "./databases/db_im_xx")
        db2 = None

        for db in self.databases:
            if db.endswith("_im.db"):
                db2 = db
                break
        
        if not db2:
            print("[Tiktok] User Messages database not found!")
            return ""

        db2 = self.access_path_file(self.internal_path, db2)
        attach = "ATTACH '{}' AS 'db2'".format(db2)

        database = Database(db1, attach = attach)
        results = database.execute_query("select UID, UNIQUE_ID, NICK_NAME, datetime(created_time/1000, 'unixepoch', 'localtime') as created_time, content as message, case when read_status = 0 then 'Not read' when read_status = 1 then 'Read' else read_status end read_not_read, local_info from SIMPLE_USER, msg where UID = sender order by created_time;")
        for entry in results:
            message={}
            message["uid"] = entry[0]
            message["uniqueid"] = entry[1]
            message["nickname"] = entry[2]
            message["createdtime"] = entry[3]
            message["message"] = entry[4]
            message["readstatus"] = entry[5]
            message["localinfo"] = entry[6]
            messagesList.append(message)
        
        print("[Tiktok] {} messages found".format(len(messagesList)))
        return messagesList

    def get_user_profile(self):
        print("[Tiktok] Get User Profile...")
        xml_file = self.access_path_file(self.internal_path, "./shared_prefs/aweme_user.xml")
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
        xml_file = self.access_path_file(self.internal_path, "./shared_prefs/search.xml")
        dump = json.loads(Utils.xml_attribute_finder(xml_file, "recent_history")["recent_history"])
        searches = []
        for i in dump: searches.append(i["keyword"])

        print("[Tiktok] {} search entrys found".format(len(searches)))
        return searches

    def get_user_profiles(self):
        print("[Tiktok] Getting User Profiles...")

        profiles = []

        db = self.access_path_file(self.internal_path, "./databases/db_im_xx")

        database = Database(db)
        results = database.execute_query("select UID, UNIQUE_ID, NICK_NAME, AVATAR_THUMB, FOLLOW_STATUS from SIMPLE_USER")
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
        return profiles

    def get_user_id(self):
        print("[Tiktok] Getting User ID")
        xml_file = self.access_path_file(self.internal_path, "./shared_prefs/iuserstate.xml")
        return Utils.xml_attribute_finder(xml_file, "userid")["userid"]

    def get_videos(self):
        print("[Tiktok] Getting Videos...")
        videos = []
        db = self.access_path_file(self.internal_path, "./databases/video.db")

        database = Database(db)
        results = database.execute_query("select key from video_http_header_t")

        for entry in results:
            videos.append(entry[0])
            self.access_path_file(self.internal_path, "./cache/cache/{}".format(entry[0]))
        print("[Tiktok] {} videos found".format(len(videos)))
        return videos
    
    def get_undark_db(self):
        print("[Tiktok] Getting undark output...")
        output = {}
        database_path = os.path.join(self.cache_path,  "internal", "databases")
        if not os.path.exists(database_path):
            return output
            
        files = os.listdir(database_path)      
        for name in files:
            listing = []
            undark_output = Utils.run_undark(os.path.join(self.cache_path,  "internal", "databases", name)).decode()
            for line in undark_output.splitlines():
                listing.append(line)
            
            if listing:
                output[name] = listing

        return output

    
    
    

        # data = self.access_path_file(self.internal_path, "./cache/cache/E21C0C16584E769C5EC2A54DF0AF786F")
        # print(data)

        