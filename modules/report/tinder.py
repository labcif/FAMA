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
        self.report["freespace"] = self.get_undark_db()
        self.report["sqlparse"] = self.get_sqlparse()
        self.report["user_photos"] = self.get_user_photos()
        self.report["bio_changes"] = self.get_bio_changes()
        self.report["messages"] = self.get_user_messages()
        self.report["credit_cards"] = self.get_credit_cards()
        self.report["locations"] = self.get_locations()

        logging.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

    
    def get_user_messages(self):
        logging.info("Getting User Messages...")

        db = os.path.join(self.internal_cache_path, "databases", "tinder-3.db")

        database = Database(db)
        messages_list =[] 
        messages = database.execute_query("select message_to_id, message_from_id , message_text, message_sent_date/1000 as message_sent_date, case when message_is_liked = 0 then 'Not liked' when message_is_liked = 1 then 'Liked' else message_is_liked end, case when message_is_seen = 0 then 'Not seen' when message_is_seen = 1 then 'Seen' else message_is_seen end, message_delivery_status from message_view order by message_sent_date;")
        
        #getting messages from conversations
        for entry in messages:
            message={}
            message["to"] = entry[0]
            message["from"] = entry[1]
            message["message"] = entry[2]
            message["created_time"] = entry[3]
            message["is_liked"] = str(entry[4])
            message["is_seen"] = str(entry[5])
            message["delivery_status"] = str(entry[6]).lower()
            messages_list.append(message)

        logging.info("{} messages found".format(len(messages_list)))

        return messages_list



    
    def get_user_photos(self):
        
        logging.info("Get User Photos...")
        db = os.path.join(self.internal_cache_path, "databases", "tinder-3.db").encode('utf-8')

        database = Database(db)
        photos_list = database.execute_query("select image_uri from profile_media;")
        user_photos =[]
        for photo in photos_list: 
            user_photos.append(photo[0])

        logging.info("{} photo(s) found".format(len(photos_list)))
        return user_photos




    def get_bio_changes(self):
        
        logging.info("Get Biography Changes...")
        db = os.path.join(self.internal_cache_path, "databases", "tinder-3.db")
        database = Database(db)
        
        biography_changes = []
        bio_list = database.execute_query("select old_bio, bio, timestamp from profile_change_bio order by timestamp")
        for entry in bio_list: 
            bio_change ={}
            bio_change["old"] = entry[0]
            bio_change["new"] = entry[1]
            bio_change["createdtime"] = entry[3]
            biography_changes.append(bio_change)
        
        logging.info("{} biography change(s) found".format(len(biography_changes)))
        return biography_changes

    def get_user_matches(self):
        logging.info("Getting User Matches...")
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
    
    def get_undark_db(self):
        logging.info("Getting undark output...")
        return Database.get_undark_output(self.databases, self.report_path)

    def get_credit_cards(self):

        logging.info("Getting User credit cards...")

        db = os.path.join(self.internal_cache_path,"app_webview","Default", "Web Data")

        

        database = Database(db)
        cards_list =[] 
        cards = database.execute_query("select name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified, origin, use_count, use_date from credit_cards;")
        
    
        for entry in cards:
            card={}
            card["name"] = entry[0]
            card["expiration_date"] = "{}/{}".format(entry[1], entry[2])
            card["card_number_encrypted"] = str(entry[3])
            card["date_modified"] = str(entry[4])
            card["origin"] = str(entry[5])
            card["use_count"] = entry[6]
            card["use_date"] = str(entry[7])
            cards_list.append(card)

        logging.info("{} credit cards found".format(len(cards_list)))

        return cards_list

    def get_locations(self):

        logging.info("Getting User locations...")

        db = os.path.join(self.internal_cache_path, "databases", "legacy_tinder-1.db")

        database = Database(db)
        locations_list =[]
        cards = database.execute_query("select latitude, longitude, state_province_long, country_short_name, country_long_name, address,route,street_number,city, last_seen_date/1000 as last_seen_date from tinder_locations;")
        
        
        for entry in cards:
            location={}
            location["latitude"] = str(entry[0])
            location["longitude"] = str(entry[1])
            location["province"] = entry[2]
            location["country_short"] = entry[3]
            location["country_long"] = entry[4]
            location["address"] = entry[5]
            location["route"] = entry[6]
            location["street_number"] = str(entry[7])
            location["city"] = entry[8]
            location["last_seen_date"] = entry[9]
            locations_list.append(location)

        logging.info("{} locations found".format(len(locations_list)))

        return locations_list

    def get_sqlparse(self):
        logging.info("Getting sqlparse...")
        return Database.get_drp_output(self.databases, self.report_path)
        


