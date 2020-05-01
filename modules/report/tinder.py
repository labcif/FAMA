import sys
import json
import os
import tarfile

from package.database import Database
from package.utils import Utils
from modules.report import ModuleParent

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)
        self.log = Utils.get_logger()
        self.log.info("Module started")
        

        
    
    def generate_report(self):

        self.report["profile"] = self.get_user_profile()
        self.report["messages"] = self.get_user_messages()
        self.report["freespace"] = self.get_undark_db()

        self.log.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

    #TIKTOK
    def get_user_messages(self):
        self.log.info("Getting User Messages...")

        db = os.path.join(self.internal_cache_path, "databases", "tinder-3")

        database = Database(db)
        messages_list =[] #each entry means 1 conversation, including participants information and messages
            #messages from conversations
        messages = database.execute_query("select message_to_id, message_from_id , message_text, message_sent_date, message_is_liked from message_view order by message_sent_date;")
        
        #getting messages from conversations
        for entry in messages:
            message={}
            message["to"] = entry[0]
            message["from"] = entry[2]
            message["message"] = entry[3]
            message["createdtime"] = entry[4]
            message["isliked"] = entry[5]
            messages_list.append(message)

        self.log.info("{} messages found".format(len(messages_list)))

        if not db in self.used_databases:
            self.used_databases.append(db)
        return messages_list

    def get_user_profile(self):
        
        self.log.info("Get Biography Changes...")
        user_profile ={}
        db = os.path.join(self.internal_cache_path, "databases", "tinder-3")
        
        database = Database(db)
        photos_list = database.execute_query("select image_uir from profile_media")
        user_profile["photos_url"] = []
        for photo in photos_list: user_profile["photos_url"].append(photo[0])

        user_profile["biography_changes"] =[]
        bio_list = database.execute_query("select old_bio, bio, timestamp from profile_change_bio order by timestamp")
        for entry in bio_list: 
            bio_change ={}
            bio_change["old"] = entry[0]
            bio_change["new"] = entry[1]
            bio_change["createdtime"] = entry[3]
            user_profile["biography_changes"].append(bio_change)


        return user_profile
    
    def get_user_uniqueid_by_id(self, uid):
        db = os.path.join(self.internal_cache_path, "databases", "db_im_xx")
        database = Database(db)
        name = database.execute_query("select UNIQUE_ID from SIMPLE_USER where uid={}".format(uid))
        if name:
            name = name[0][0]
        else:
            name = None
        return name
        








    def get_user_searches(self):
        self.log.info("Getting User Search History...")
        
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "search.xml")
        searches = []
        #verify if recent hisotry tag exists
        try:
            dump = json.loads(Utils.xml_attribute_finder(xml_file, "recent_history")["recent_history"])
            for i in dump: searches.append(i["keyword"])
        except:
            pass

        self.log.info("{} search entrys found".format(len(searches)))
        return searches


    def get_user_matches(self):
        self.log.info("Getting User Profiles...")
        matches = {}

        db = os.path.join(self.internal_cache_path, "databases", "tinder-3.db")

        database = Database(db)
        results = database.execute_query("select match_id, match_creation_date, match_last_activity_date, match_person_id, match_person_name, match_person_bio, match_person_birth_date,  case when match_is_blocked = 1 then 'Blocked' when match_is_blocked = 0 then 'Not Blocked ' else 'Invalid' end from match_view")
        for entry in results:
            match={}
            match["id"] = entry[0]
            match["creation_date"] = entry[1]
            match["last_activity_date"] = entry[2]
            match["person_id"] = entry[3]
            match["person_name"] = entry[4]
            match["person_bio"] = entry[5]
            match["person_bithdate"] = entry[6]
            match["person_bithdate"] = entry[7]
            match["is_blocked"] = entry[8]
            matches[match["id"]] = match

        if not db in self.used_databases:
            self.used_databases.append(db)

        self.log.info("{} matches found".format(len(matches)))
        return matches
    
    
    



    def get_user_id(self):
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "iuserstate.xml")
        return Utils.xml_attribute_finder(xml_file, "userid")["userid"]

    def get_videos(self):
        self.log.info("Getting Videos...")
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
                    video["last_modified"] = Utils.date_parser(line.split(": ")[1], "%a, %d %b %Y %H:%M:%S %Z")
                    break
            videos.append(video)
            #self.access_path_file(self.internal_path, "./cache/cache/{}".format(entry[0]))
        
        if not db in self.used_databases:
            self.used_databases.append(db)

        self.log.info("{} video(s) found".format(len(videos)))
        return videos
    
    def get_undark_db(self):
        self.log.info("Getting undark output...")
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
        self.log.info("Getting published videos")
        videos = []
        base_path = os.path.join(self.internal_cache_path, "cache", "aweme_publish")
        aweme_publish_files = os.listdir(base_path)

        for aweme_file in aweme_publish_files:
            dump = Utils.read_json(os.path.join(base_path, aweme_file))
            aweme_list = dump.get("aweme_list")
            if aweme_list:
                for entry in aweme_list:
                    video ={}
                    video["created_time"] = entry.get("create_time")
                    video["video"] = entry.get("video").get("animated_cover").get("url_list")[0]
                    videos.append(video)
    
        self.log.info("{} video(s) found".format(len(videos)))
        return videos


    
    def get_last_session(self):
        self.log.info("Getting last session...")
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
            session_entry["time"] = Utils.date_parser(entry[2], "%Y-%m-%d %H:%M:%S")
            session_entry["session_id"] = entry[3]
            session.append(session_entry)

            #json body parser
            body = {}
            for key, value in body_dump.items():     
                if key in relevant_keys:
                    body[key] = value
            
            session_entry["body"] =body

        self.log.info("{} entrys found".format(len(results)))
        return session

