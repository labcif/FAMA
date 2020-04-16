import sys
import json
import os
import tarfile
import logging

from package.database import Database
from package.utils import Utils
from package.timeline import Timeline
from modules.report import ModuleParent

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)

        self.timeline = Timeline()
        logging.info("Module started")
    
    def generate_report(self):
        self.report["freespace"] = self.get_undark_db()
        self.report["profile"] = self.get_user_profile()
        self.report["messages"] = self.get_user_messages()
        self.report["users"] = self.get_user_profiles()
        self.report["searches"] = self.get_user_searches()
        self.report["videos"] = self.get_videos()
        self.report["published_videos"] = self.get_videos_publish()
        self.report["log"] = self.get_last_session()
        self.report["timeline"] = self.timeline.get_sorted_timeline()

        logging.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

    #TIKTOK
    def get_user_messages(self):
        logging.info("Getting User Messages...")
        
        # db1 = os.path.join(self.internal_cache_path, "databases", "db_im_xx")
        # db2 = None

        for db in self.databases:
            if db.endswith("_im.db"):
                db1 = db
                break
        
        # if not db2:
        #     print("[Tiktok] User Messages database not found!")
        #     return ""

        # db2 = os.path.join(self.internal_path, db2)
        # attach = "ATTACH '{}' AS 'db2'".format(db2)

        database = Database(db1)
        
        conversations_list =[] #each entry means 1 conversation, including participants information and messages

        conversations_ids_list = database.execute_query("select conversation_id from conversation_core") #list if conversations

        for conversation in conversations_ids_list:
            conversation_output={}

            id1 = conversation[0].split(':')[2]
            id2 = conversation[0].split(':')[3]

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
                message_type = entry[4]

                message_dump = json.loads(entry[1])
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
                    message["type"] = "unknown"
                    body= str(message_dump)
                
                message["message"] = body
                message["deleted"] = str(entry[5])
                conversation_output["messages"].append(message)

                timeline_event = {}
                timeline_event["event"]= "Message"
                timeline_event["from"]= message["sender"]
                timeline_event["to"]= message["receiver"]
                timeline_event["message"]= message["message"]
                self.timeline.add(message["createdtime"], timeline_event)
            
            #adding conversation and participants information to main array
            conversations_list.append(conversation_output)

        logging.info("{} messages found".format(len(conversation_output.get("messages"))))

        return conversations_list

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
                    user_profile[index] = dump[index]
                break
            
        user_profile["url"] = "https://www.tiktok.com/@{}".format(user_profile["unique_id"])
        
        
        timeline_event = {}
        timeline_event["event"]= "User resgistration"
        timeline_event["uniqueid"] = user_profile["unique_id"] 
        timeline_event["url"]= user_profile["url"]

        self.timeline.add(user_profile["register_time"], timeline_event)
        
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
                    timeline_event["event"]= "Video loaded"
                    timeline_event["video"]= video["key"]

                    self.timeline.add(video["last_modified"], timeline_event)
                    break
            videos.append(video)
        
        logging.info("{} video(s) found".format(len(videos)))
        return videos
    
    def get_undark_db(self):
        logging.info("Getting undark output...")
        return Database.get_undark_output(self.databases, self.report_path)
    

    def get_videos_publish(self):
        logging.info("Getting published videos")
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
                    
                    
                    timeline_event = {}
                    timeline_event["event"]= "Video Published"
                    timeline_event["url"]= video["video"]
                    
                    self.timeline.add(video["created_time"], timeline_event)
                    videos.append(video)
    
        logging.info("{} video(s) found".format(len(videos)))
        return videos


    
    def get_last_session(self):
        logging.info("Getting last session...")
        session = []

        relevant_keys = ["page", "request_method", "is_first","duration","is_first","rip","duration","author_id","access2","video_duration","video_quality","access",
        "page_uid","previous_page","enter_method","enter_page","key_word","search_keyword","next_tab","search_type", "play_duration", "content"]

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
            timeline_event["event"]= "System Action"
            timeline_event["action"]= session_entry["action"]
            
            self.timeline.add(session_entry["time"], timeline_event)
            
            session.append(session_entry)

            #json body parser
            body = {}
            for key, value in body_dump.items():     
                if key in relevant_keys:
                    body[key] = value
            
            session_entry["body"] =body

        logging.info("{} entrys found".format(len(results)))
        return session

