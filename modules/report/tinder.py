import sys
import json
import os
import tarfile
import logging

from package.database import Database
from package.utils import Utils
from modules.report import ModuleParent

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)
        logging.info("Module started")
        
    def generate_report(self):
        #self.report["profile"] = self.get_user_profile()
        self.report["messages"] = self.get_user_messages()
        #self.report["freespace"] = self.get_undark_db()

        logging.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

    #TIKTOK
    def get_user_messages(self):
        logging.info("Getting User Messages...")

        db = os.path.join(self.internal_cache_path, "databases", "tinder-3.db")

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
            #message["isliked"] = entry[5]
            messages_list.append(message)

        logging.info("{} messages found".format(len(messages_list)))

        #if not db in self.used_databases:
        #    self.used_databases.append(db)
        return messages_list

    def get_user_profile(self):
        
        logging.info("Get Biography Changes...")
        user_profile ={}
        db = os.path.join(self.internal_cache_path, "databases", "tinder-3.db")
        
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

    def get_user_matches(self):
        logging.info("Getting User Profiles...")
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

        logging.info("{} matches found".format(len(matches)))
        return matches

