import logging

from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.datamodel import Relationship
from org.sleuthkit.datamodel import Account
from org.sleuthkit.autopsy.geolocation.datamodel import BookmarkWaypoint

from package.database import Database
from package.utils import Utils

from modules.autopsy import ModulePsyParent

class ModulePsy(ModulePsyParent):
    def __init__(self, module_name):
        ModulePsyParent.__init__(self, module_name)

    def process_report(self, datasource_name, file, report_number, path):
        if self.context.isJobCancelled():
            return IngestModule.ProcessResult.OK
        
        #TODO
        # HERE WE CAN CALL THE FUNCTIONS THAT WILL INDEX THE REPORT'S ARTIFACTS
        data = Utils.read_json(path)
        self.process_messages(data.get("messages"), file)
        self.process_user_photos(data.get("user_photos"), file)
        self.process_bio_changes(data.get("bio_changes"), file)
        self.process_user_matches(data.get("matches"), file)
        self.process_credit_cards(data.get("credit_cards"), file)
        self.process_locations(data.get("locations"), file)
        self.process_drp(data.get("sqlparse"), file)
        self.process_undark(data.get("freespace"), file)

    def initialize(self, context):
        self.context = context

        # HERE YOU CAN DEFINE THE ARTIFACTS TO DISPLAY ON THE BLACKBOARD
        self.art_user_profile = self.utils.create_artifact_type(self.module_name, "TINDER_PROFILE", "Profile")
        self.art_messages = self.utils.create_artifact_type(self.module_name, "TINDER_MESSAGES","Messages")
        self.art_locations = self.utils.create_artifact_type(self.module_name, "TINDER_LOCATIONS","Locations")
        self.art_matches = self.utils.create_artifact_type(self.module_name, "TINDER_MATCHES","Matches")
        self.art_credit_cards = self.utils.create_artifact_type(self.module_name, "TINDER_CREDIT_CARDS","Credit Cards")
        self.art_bio_changes = self.utils.create_artifact_type(self.module_name, "TINDER_BIO_CHANGES","Biography Changes")
        self.art_deleted_rows = self.utils.create_artifact_type(self.module_name, "TINDER_DELETED_ROWS", "Deleted rows")
        self.art_photos = self.utils.create_artifact_type(self.module_name, "TINDER_PHOTOS", "Photos")

        

        self.account_tinder = self.utils.add_account_type("Tinder", "Tinder")
        


        # MESSAGE ATTRIBUTES
        self.att_msg_to = self.utils.create_attribute_type('TINDER_MSG_TO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "To")
        self.att_msg_from = self.utils.create_attribute_type('TINDER_MSG_FROM', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "From")
        self.att_msg_message = self.utils.create_attribute_type('TINDER_MSG_MESSAGE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Message")
        self.att_msg_created_time = self.utils.create_attribute_type('TINDER_MSG_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Created time")
        self.att_msg_like = self.utils.create_attribute_type('TINDER_MSG_LIKE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Like")
        self.att_msg_seen = self.utils.create_attribute_type('TINDER_MSG_SEEN', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Seen")
        self.att_msg_delivery_status = self.utils.create_attribute_type('TINDER_DELIVERY_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Delivery status")

        # LOCATION ATTRIBUTES
        self.att_loc_latitude = self.utils.create_attribute_type('TINDER_LOC_LATITUDE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Latitude")
        self.att_loc_longitude = self.utils.create_attribute_type('TINDER_LOC_LONGITUDE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Longitude")
        self.att_loc_province = self.utils.create_attribute_type('TINDER_LOC_PROVINCE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Province")
        self.att_loc_country_short= self.utils.create_attribute_type('TINDER_LOC_COUNTRY_SHORT', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Country Short")
        self.att_loc_country = self.utils.create_attribute_type('TINDER_LOC_COUNTRY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Country")
        self.att_loc_address = self.utils.create_attribute_type('TINDER_LOC_ADDRESS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Address")
        self.att_loc_route = self.utils.create_attribute_type('TINDER_LOC_ROUTE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Route")
        self.att_loc_street_number = self.utils.create_attribute_type('TINDER_LOC_STREET_NUMBER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Street Number")
        self.att_loc_city = self.utils.create_attribute_type('TINDER_LOC_CITY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "City")
        self.att_loc_last_seen = self.utils.create_attribute_type('TINDER_LOC_LAST_SEEN', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Last Seen Date")
        
        # CREDIT CARDS ATTRIBUTES
        self.att_card_name = self.utils.create_attribute_type('TINDER_CARD_NAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Card Name")
        self.att_card_expiration_date = self.utils.create_attribute_type('TINDER_CARD_EXPIRATION', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Card Expiration")
        self.att_card_card_number_encrypted = self.utils.create_attribute_type('TINDER_CARD_NUMBER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Encrypted Card Number ")
        self.att_card_date_modified = self.utils.create_attribute_type('TINDER_CARD_DATE_MODIFIED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Date Modified")
        self.att_card_origin = self.utils.create_attribute_type('TINDER_CARD_ORIGIN', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Origin")
        self.att_card_use_count = self.utils.create_attribute_type('TINDER_CARD_USE_COUNT', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Use Count")
        self.att_card_use_date = self.utils.create_attribute_type('TINDER_CARD_USE_DATE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Use Date")
        
        # BIOGRAPHY CHANGES ATTRIBUTES
        self.att_bio_old = self.utils.create_attribute_type('TINDER_BIO_OLD', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Old Biography")
        self.att_bio_new = self.utils.create_attribute_type('TINDER_BIO_NEW', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "New Biography")
        self.att_bio_created_time = self.utils.create_attribute_type('TINDER_BIO_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Created Time")
        

        

        # MATCH ATTRIBUTES
        self.att_match_id = self.utils.create_attribute_type('TINDER_MATCH_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "ID")
        self.att_match_creattion_date = self.utils.create_attribute_type('TINDER_MATCH_CREATION_DATE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Creation Date")
        self.att_match_last_activity = self.utils.create_attribute_type('TINDER_MATCH_LAST_ACTIVITY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Last Activity")
        self.att_match_person_id = self.utils.create_attribute_type('TINDER_MATCH_PERSON_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Person ID")
        self.att_match_person_name = self.utils.create_attribute_type('TINDER_MATCH_PERSON_NAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Person Name")
        self.att_match_person_biography = self.utils.create_attribute_type('TINDER_MATCH_PERSON_BIO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Person Biography")
        self.att_match_person_birthday = self.utils.create_attribute_type('TINDER_MATCH_PERSON_BIRTHDAY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Person Birthdate")
        self.att_match_block = self.utils.create_attribute_type('TINDER_MATCH_BLOCK', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Block")

        #DELETED ROWS
        self.att_dr_key = self.utils.create_attribute_type('TINDER_DELETED_ROWS_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Database")
        self.att_dr_method = self.utils.create_attribute_type('TINDER_DELETED_ROWS_METHOD', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Method")
        self.att_dr_type = self.utils.create_attribute_type('TINDER_DELETED_ROWS_TYPE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Type")
        self.att_dr_offset = self.utils.create_attribute_type('TINDER_DELETED_ROWS_OFFSET', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Offset")
        self.att_dr_length = self.utils.create_attribute_type('TINDER_DELETED_ROWS_LENGTH', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Length")
        self.att_dr_unallocated = self.utils.create_attribute_type('TTINDER_DELETED_ROWS_UNALLOCATED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unallocated")
        self.att_dr_data = self.utils.create_attribute_type('TINDER_DELETED_ROWS_DATA', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Data")

        
        

        # PHOTOS
        self.att_ph_avatar = self.utils.create_attribute_type('TINDER_PROFILE_AVATAR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Avatar")


    def process_messages(self, messages, file):
        logging.info("Indexing user messages")
        if not messages:
            return

        
        for message in messages:
            try:
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_MESSAGE)
                
        # THIS IS USEFUL FOR THE AUTOPSY COMMUNICATIONS TAB
        
                contact_1 = self.utils.get_or_create_account(self.account_tinder, file, message.get("from"))
                contact_2 = self.utils.get_or_create_account(self.account_tinder, file, message.get("to"))
        
                art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_FROM, "tinder-3.db", message.get("from")))
                art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_TO, "tinder-3.db", message.get("to")))
                art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_TEXT, "tinder-3.db", message.get("message")))
                art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, "tinder-3.db", message.get("created_time")))
                art.addAttribute(BlackboardAttribute(self.att_msg_like, "tinder-3.db", message.get("is_liked")))
                art.addAttribute(BlackboardAttribute(self.att_msg_seen, "tinder-3.db", message.get("is_seen")))
                art.addAttribute(BlackboardAttribute(self.att_msg_delivery_status, "tinder-3.db", message.get("delivery_status")))
        
        # THIS IS USEFUL FOR THE AUTOPSY COMMUNICATIONS TAB
        
                self.utils.add_relationship(contact_1, [contact_2], art, Relationship.Type.MESSAGE, message.get("created_time"))
                self.utils.index_artifact(art, BlackboardArtifact.ARTIFACT_TYPE.TSK_MESSAGE)
        
            except Exception as e:
                logging.warning("Error getting a message: " + str(e))

    def process_user_matches(self, matches, file):
        logging.info("Indexing user matches")
        if not matches:
            return
        
        for match in matches:
            try:
                art = file.newArtifact(self.art_matches.getTypeID())
                

                art.addAttribute(BlackboardAttribute(self.att_match_id, "tinder-3.db", match.get("id")))
                art.addAttribute(BlackboardAttribute(self.att_match_creattion_date, "tinder-3.db", match.get("creation_date")))
                art.addAttribute(BlackboardAttribute(self.att_match_last_activity, "tinder-3.db", match.get("last_activity_date")))
                art.addAttribute(BlackboardAttribute(self.att_match_person_id, "tinder-3.db", match.get("person_id")))
                art.addAttribute(BlackboardAttribute(self.att_match_person_name, "tinder-3.db", match.get("person_name")))
                art.addAttribute(BlackboardAttribute(self.att_match_person_biography, "tinder-3.db", match.get("person_bio")))
                art.addAttribute(BlackboardAttribute(self.att_match_person_birthday, "tinder-3.db", match.get("person_bithdate")))
                art.addAttribute(BlackboardAttribute(self.att_match_block, "tinder-3.db", match.get("is_blocked")))

                self.utils.index_artifact(art, self.art_matches)
            except Exception as e:
                logging.warning("Error getting user macth: " + str(e))


    def process_locations(self, locations, file):
        logging.info("Indexing user locations")
        if not locations:
            return
        
        for location in locations:
            try:
                art = file.newArtifact(self.art_locations.getTypeID())
        
                art.addAttribute(BlackboardAttribute(self.att_loc_latitude, "legacy_tinder-1.db", str(location.get("latitude"))))
                art.addAttribute(BlackboardAttribute(self.att_loc_longitude, "legacy_tinder-1.db", str(location.get("longitude"))))
                art.addAttribute(BlackboardAttribute(self.att_loc_province, "legacy_tinder-1.db", location.get("province")))
                art.addAttribute(BlackboardAttribute(self.att_loc_country_short, "legacy_tinder-1.db", location.get("country_short")))
                art.addAttribute(BlackboardAttribute(self.att_loc_country, "legacy_tinder-1.db", location.get("country_long")))
                art.addAttribute(BlackboardAttribute(self.att_loc_address, "legacy_tinder-1.db", location.get("address")))
                art.addAttribute(BlackboardAttribute(self.att_loc_route, "legacy_tinder-1.db", location.get("route")))
                art.addAttribute(BlackboardAttribute(self.att_loc_street_number, "legacy_tinder-1.db", location.get("street_number")))
                art.addAttribute(BlackboardAttribute(self.att_loc_city, "legacy_tinder-1.db", location.get("city")))
                art.addAttribute(BlackboardAttribute(self.att_loc_last_seen, "legacy_tinder-1.db", location.get("last_seen_date")))

                self.utils.add_tracking_point(file, location.get("last_seen_date"), location.get("latitude"), location.get("longitude"),0,"legacy_tinder-1.db")
                self.utils.index_artifact(art, self.art_locations)

            except Exception as e:
                logging.warning("Error getting location: " + str(e))

    def process_user_photos(self, photos, file):
        logging.info("Indexing user photos")
        if not photos:
            return
        
        for photo in photos:
            try:
                art = file.newArtifact(self.art_photos.getTypeID())
                art.addAttribute(BlackboardAttribute(self.att_ph_avatar, "tinder-3.db", str(photo)))

                self.utils.index_artifact(art, self.art_photos)
            except Exception as e:
                logging.warning("Error getting user photo: " + str(e))

    
    def process_bio_changes(self, bio_changes, file):
        logging.info("Indexing user biography changes")
        if not bio_changes:
            return
        
        for change in bio_changes:
            try:
                art = file.newArtifact(self.art_bio_changes.getTypeID())
        
                art.addAttribute(BlackboardAttribute(self.att_bio_old, "tinder-3.db", change.get("old")))
                art.addAttribute(BlackboardAttribute(self.att_bio_new, "tinder-3.db", change.get("new")))
                art.addAttribute(BlackboardAttribute(self.att_bio_created_time, "tinder-3.db", change.get("createdtime")))

                self.utils.index_artifact(art, self.art_bio_changes)
            except Exception as e:
                logging.warning("Error getting biography change: " + str(e))


    def process_credit_cards(self, cards, file):
        logging.info("Indexing user credit cards")
        if not cards:
            return

        for card in cards:
            try:
                art = file.newArtifact(self.art_credit_cards.getTypeID())
                
                art.addAttribute(BlackboardAttribute(self.att_msg_from, "Web Data", card.get("name")))
                art.addAttribute(BlackboardAttribute(self.att_msg_to, "Web Data", card.get("expiration_date")))
                art.addAttribute(BlackboardAttribute(self.att_msg_message, "Web Data", card.get("card_number_encrypted")))
                art.addAttribute(BlackboardAttribute(self.att_msg_created_time, "Web Data", card.get("date_modified")))
                art.addAttribute(BlackboardAttribute(self.att_msg_like, "Web Data", card.get("origin")))
                art.addAttribute(BlackboardAttribute(self.att_msg_seen, "Web Data", card.get("use_count")))
                art.addAttribute(BlackboardAttribute(self.att_msg_delivery_status, "Web Data", card.get("use_date")))

                self.utils.index_artifact(art, self.art_credit_cards)
            except Exception as e:
                logging.warning("Error getting credit card: " + str(e))

    def process_undark(self, undarks, file):
        logging.info("Indexing undark output.")
        if not undarks:
            return
        for database, deleted_rows in undarks.items():
            for row in deleted_rows:
                try: 
                    art = file.newArtifact(self.art_deleted_rows.getTypeID())
                    attributes = []
                    attributes.append(BlackboardAttribute(self.att_dr_key, database, database))
                    attributes.append(BlackboardAttribute(self.att_dr_method, database, "Undark"))
                    attributes.append(BlackboardAttribute(self.att_dr_data, database, row))
                    art.addAttributes(attributes)
                    self.utils.index_artifact(art, self.art_deleted_rows)        
                except Exception as e:
                    logging.warning("Error indexing undark output: " + str(e))


    def process_drp(self, drps, file):
        logging.info("Indexing drp output.")
        if not drps:
            return
        for database, deleted_rows in drps.items():
            for row in deleted_rows:
                try: 
                    art = file.newArtifact(self.art_deleted_rows.getTypeID())
                    attributes = []
                    attributes.append(BlackboardAttribute(self.att_dr_key, database, database))
                    attributes.append(BlackboardAttribute(self.att_dr_method, database, "SQLite-Deleted-Records-Parser"))
                    attributes.append(BlackboardAttribute(self.att_dr_type, database, row.get("type")))
                    attributes.append(BlackboardAttribute(self.att_dr_offset, database, row.get("offset")))
                    attributes.append(BlackboardAttribute(self.att_dr_length, database, row.get("length")))
                    attributes.append(BlackboardAttribute(self.att_dr_unallocated, database, row.get("unallocated")))
                    attributes.append(BlackboardAttribute(self.att_dr_data, database, row.get("data")))

                    art.addAttributes(attributes)
                    self.utils.index_artifact(art, self.art_deleted_rows) 
                except Exception as e:
                    logging.warning("Error indexing drp output: " + str(e))
    