import json
import os
import tarfile
import logging

from package.database import Database
from package.utils import Utils
from package.models import Timeline, Location, Media
from package.mdlfixer import MDLFixer
from modules.report import ModuleParent

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)

        self.timeline = Timeline()
        self.media = Media()
        logging.info("Module started")
    
    def generate_report(self):
        self.report["freespace"] = self.get_info(self.get_undark_db)
        self.report["sqlparse"] = self.get_info(self.get_sqlparse)
        self.report["profile"] = self.get_info(self.get_user_profile)
        self.report["messages"] = self.get_info(self.get_user_messages)
        self.report["users"] = self.get_info(self.get_user_profiles)
        self.report["logged_users"] = self.get_info(self.get_logged_users)

        self.report["searches"] = self.get_info(self.get_user_searches)
        self.report["videos"] = self.get_info(self.get_videos)
        self.report["published_videos"] = self.get_info(self.get_videos_publish)
        self.report["log"] = self.get_info(self.get_last_session)
        self.report["cache_images"] = self.get_info(self.get_fresco_cache)
        self.report["open_events"] = self.get_info(self.get_open_events)
        
        self.add_model(self.timeline)
        self.add_model(self.media)

        logging.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

    #TIKTOK
    def get_user_messages(self):
        logging.info("Getting User Messages...")
        
        # db1 = os.path.join(self.internal_cache_path, "databases", "db_im_xx")
        # db2 = None
        
        # if not db2:
        #     print("[Tiktok] User Messages database not found!")
        #     return ""

        # db2 = os.path.join(self.internal_path, db2)
        # attach = "ATTACH '{}' AS 'db2'".format(db2)
        
        conversations_list =[] #each entry means 1 conversation, including participants information and messages

        for db in self.databases:
            if not db.endswith("_im.db"):
                continue
            
            database = Database(db)

            conversations_ids_list = database.execute_query("select conversation_id from conversation_core") #list if conversations

            for conversation in conversations_ids_list:
                conversation_output={}

                id1 = conversation[0].split(':')[2]
                id2 = conversation[0].split(':')[3]

                conversation_output["database"] = os.path.basename(db)
                conversation_output["participant_1"] = self.get_user_uniqueid_by_id(id1)
                conversation_output["participant_2"] = self.get_user_uniqueid_by_id(id2)
                conversation_output["messages"] = []
                
                #messages from conversations
                messages_list = database.execute_query("select created_time/1000 as created_time, content as message, case when read_status = 0 then 'Not read' when read_status = 1 then 'Read' else read_status end read_not_read, local_info, type, case when deleted = 0 then 'Not deleted' when deleted = 1 then 'Deleted' else deleted end, sender from msg where conversation_id='{}' order by created_time;".format(conversation[0]))
                
                #getting messages from conversations
                for entry in messages_list:
                    message={}
                    message["createdtime"] = entry[0]
                    message["readstatus"] = str(entry[2])
                    message["localinfo"] = entry[3]
                    if entry[6] == int(id1):
                        message["sender"] = conversation_output["participant_1"]
                        message["receiver"] = conversation_output["participant_2"]
                    else:
                        message["sender"] = conversation_output["participant_2"]
                        message["receiver"] = conversation_output["participant_1"]

                    message["type"] = self.get_message_type_by_id(entry[4])                
                    message["message"] = self.parse_body_message_by_id(entry[4], json.loads(entry[1]))
                    message["deleted"] = str(entry[5])
                    conversation_output["messages"].append(message)

                    timeline_event = {}
                    timeline_event["from"]= message["sender"]
                    timeline_event["to"]= message["receiver"]
                    timeline_event["message"]= message["message"]
                    self.timeline.add(message["createdtime"],"AF_message", timeline_event)
                
                #adding conversation and participants information to main array
                conversations_list.append(conversation_output)

        logging.info("{} messages found".format(len(conversation_output.get("messages"))))

        return conversations_list

    def get_logged_users(self):
        
        logging.info("Get User Profile...")
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "aweme_user.xml")
        user_profiles=[]
        user_profile ={}
        values = Utils.xml_attribute_finder(xml_file)
        for key, value in values.items():
            if key.endswith("_significant_user_info"):
                user_profile ={}
                dump=json.loads(value)
                atributes =["uid", "short_id","unique_id", "nickname", "nickname", "avatar_url"]

                for index in atributes:
                    user_profile[index] = dump.get(index)
                if user_profile.get("unique_id"):
                    user_profile["url"] = "https://www.tiktok.com/@{}".format(user_profile["unique_id"])
                
                user_profiles.append(user_profile)
        
        return user_profiles



    def get_open_events(self):
        logging.info("Get application open events...")
        
        open_events=[]
        db = os.path.join(self.internal_cache_path, "databases", "TIKTOK.db")
        database = Database(db)
        results = database.execute_query("select open_time/1000 from app_open;")

        for event in results:
            open_events.append(event[0])
            timeline_event = {}
            timeline_event["event"]= "Open Application"
            self.timeline.add(event[0],"AF_system", timeline_event)
        
        return open_events





    def get_user_profile(self):
        
        logging.info("Get User Profile...")
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "aweme_user.xml")
        user_profile ={}
        values = Utils.xml_attribute_finder(xml_file)
        for key, value in values.items():
            if key.endswith("_aweme_user_info"):
                #try:
                dump=json.loads(value)
                atributes =["account_region", "follower_count","following_count", "gender", "google_account", "is_blocked", "is_minor", "nickname", "register_time", "sec_uid", "short_id", "uid", "unique_id"]

                for index in atributes:
                    user_profile[index] = dump.get(index)
                break
            
        if user_profile.get("unique_id"):
            user_profile["url"] = "https://www.tiktok.com/@{}".format(user_profile["unique_id"])
        
        
        if user_profile.get("uniqueid") and user_profile.get("url"):
            timeline_event = {}
            timeline_event["uniqueid"] = user_profile["unique_id"] 
            timeline_event["url"]= user_profile["url"]

            self.timeline.add(user_profile["register_time"],"AF_user", timeline_event)
        
        return user_profile
    
    def get_user_uniqueid_by_id(self, uid):
        db = os.path.join(self.internal_cache_path, "databases", "db_im_xx")
        database = Database(db)
        name = database.execute_query("select UNIQUE_ID from SIMPLE_USER where uid={}".format(uid))
        if name:
            name = name[0][0]
        else:
            name = str(uid)
        return name
        
    def get_user_searches(self):
        logging.info("Getting User Search History...")
        
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "search.xml")
        searches = []
        #verify if recent hisotry tag exists
        try:
            dump = json.loads(Utils.xml_attribute_finder(xml_file, "recent_history")["recent_history"])
            for i in dump: searches.append(i["keyword"])
        except:
            pass

        logging.info("{} search entrys found".format(len(searches)))
        return searches


    def get_user_profiles(self):
        logging.info("Getting User Profiles...")
        profiles = {}

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
            profiles[message["uniqueid"]] = message

        logging.info("{} profiles found".format(len(profiles.keys())))
        return profiles

    def get_user_id(self):
        xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "iuserstate.xml")
        return Utils.xml_attribute_finder(xml_file, "userid")["userid"]

    def get_videos(self):
        logging.info("Getting Videos...")
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
                    

                    timeline_event = {}
                    timeline_event["video"]= video["key"]

                    self.timeline.add(video["last_modified"],"AF_video", timeline_event)
                    break
            self.media.add(os.path.join(self.internal_cache_path, "cache", "cache", video["key"] ))
            videos.append(video)

        for entry in MDLFixer.folder_scanner(os.path.join(self.internal_cache_path, "cache", "cachev2")):
            self.media.add(os.path.join(self.internal_cache_path, "cache", "cachev2", entry))

            video = {}
            video["key"] = os.path.basename(entry)
            video["last_modified"] = 0
            videos.append(video)
        
        logging.info("{} video(s) found".format(len(videos)))
        return videos
    
    def get_undark_db(self):
        logging.info("Getting undark output...")
        return Database.get_undark_output(self.databases, self.report_path)

    def get_sqlparse(self):
        logging.info("Getting sqlparse...")
        return Database.get_drp_output(self.databases, self.report_path)

    def get_videos_publish(self):
        logging.info("Getting published videos")
        videos = []
        base_path = os.path.join(self.internal_cache_path, "cache", "aweme_publish")
        if not os.path.exists(base_path):
            return videos

        aweme_publish_files = os.listdir(base_path)

        for aweme_file in aweme_publish_files:
            dump = Utils.read_json(os.path.join(base_path, aweme_file))
            aweme_list = dump.get("aweme_list")
            if aweme_list:
                for entry in aweme_list:
                    video ={}
                    video["created_time"] = entry.get("create_time")
                    # if entry.get("video"):
                    #     if entry.get("video").get("animated_cover"):
                    #         if entry.get("video").get("animated_cover").get("url_list"):
                    #             video["video"] = str(entry.get("video").get("animated_cover").get("url_list")[0])
                    #         else:
                    #             video["video"] = entry.get("video").get("animated_cover")
                    #     else:
                    #         video["video"] = entry.get("video")

                    video["video"] = ""
                    video["duration"] = ""
                    video["cover"] = ""
                    video["api_address"] = ""

                    if entry.get("video"):
                        if entry.get("video").get("animated_cover"):
                            video["video"] =entry.get("video").get("animated_cover").get("url_list")[0]
                        else:
                            video["video"] =str(entry)

                        video["duration"] = entry.get("video").get("duration")
                        
                        try:
                            video["cover"] = str(entry.get("video").get("cover").get("url_list")[0])
                        except:
                            pass
                        try:
                            video["api_address"] = entry.get("video").get("play_addr").get("url_list")[-1]
                        except:
                            pass

                    video["share_url"] = entry.get("share_url")
                    video["music"] = entry.get("music").get("play_url").get("url_list")[0]
                    
                    timeline_event = {}
                    timeline_event["url"] = video["video"]
                    
                    self.timeline.add(video["created_time"],"AF_publish", timeline_event)
                    videos.append(video)
    
        logging.info("{} video(s) found".format(len(videos)))
        return videos

    def get_fresco_cache(self):
        logging.info("Getting cache...")
        cache_path = os.path.join(self.external_cache_path, "cache", "picture","fresco_cache", "v2.ols100.1") 
        numerate_dirs = os.listdir(cache_path)
        fresco_images =[]

        for directory in numerate_dirs:
            for cache_file in os.listdir(os.path.join(cache_path, directory)):
                fresco_images.append(cache_file)
                self.media.add(os.path.join(cache_path, directory, cache_file))
        
        logging.info("{} cache file(s) found".format(len(fresco_images)))
        return fresco_images


    
    def get_last_session(self):
        logging.info("Getting last session...")
        session = []

        relevant_keys = ["device","name","status","ab_sdk_version","storage_available_internal_size","storage_available_external_size","app_storage_size","brand","page", "request_method", "is_first","duration","is_first","rip","duration","author_id","access2","video_duration","video_quality","access",
        "page_uid","previous_page","enter_method","enter_page","key_word","search_keyword","next_tab","search_type", "play_duration", "content", "manufacturer","os_version"]

        db = os.path.join(self.internal_cache_path, "databases", "ss_app_log.db")
        database = Database(db)
        results = database.execute_query("select tag, ext_json, datetime(timestamp/1000, 'unixepoch', 'localtime'), session_id from event order by timestamp")
        
        for entry in results:
            session_entry={}
            session_entry["action"] = entry[0]
            
            body_dump = json.loads(entry[1])
            session_entry["time"] = Utils.date_parser(entry[2], "%Y-%m-%d %H:%M:%S")
            session_entry["session_id"] = entry[3]
            
            timeline_event = {}
            timeline_event["action"]= session_entry["action"]
            
            self.timeline.add(session_entry["time"],"AF_system", timeline_event)
            
            session.append(session_entry)

            #json body parser
            body = {}
            for key, value in body_dump.items():     
                if key in relevant_keys:
                    body[key] = value
            
            session_entry["body"] =body

        logging.info("{} entrys found".format(len(results)))
        return session
    
    @staticmethod

    def parse_body_message_by_id(message_type, message_dump):
        body=""
        if  message_type == 7:
            body = message_dump.get("text")
        elif message_type == 8:
            body= "https://www.tiktok.com/@tiktok/video/{}".format(message_dump.get("itemId"))
        elif message_type == 5:
            body=message_dump.get("url").get("url_list")[0]
        elif message_type == 15:
            body=message_dump.get("joker_stickers")[0].get("static_url").get("url_list")[0]
        elif message_type == 25:
            body = "https://www.tiktok.com/@{}".format(message_dump.get("desc")) # or body = "https://m.tiktok.com/h5/share/usr/{}.html".format(message_dump.get("uid"))
        elif message_type == 19:
            body = message_dump.get("push_detail")
        elif message_type == 22:
            body = "https://www.tiktok.com/music/tiktok-{}".format(message_dump.get("music_id"))
        else:
            body= str(message_dump)
        
        return body


    @staticmethod
    def get_message_type_by_id(message_type_id):
        if  message_type_id == 7: return "text"
        if  message_type_id == 8: return "video"
        if  message_type_id == 5: return "gif"
        if  message_type_id == 15: return "gif"
        if  message_type_id == 22: return "audio"
        if  message_type_id == 25: return "profile"
        if  message_type_id == 19: return "hashtag"
        return "unknown"



