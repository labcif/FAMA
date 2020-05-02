import sys
import os
import logging

from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.datamodel import Relationship
from org.sleuthkit.datamodel import Account

from package.utils import Utils

from modules.autopsy import ModulePsyParent

class ModulePsy(ModulePsyParent):
    def __init__(self, module_name):
        ModulePsyParent.__init__(self, module_name)

    def process_report(self, datasource_name, file, report_number, path):
        # Check if the user pressed cancel while we were busy
        if self.context.isJobCancelled():
            return IngestModule.ProcessResult.OK

        data = Utils.read_json(path)
        
        self.uid = data.get("profile").get("uid")

        self.process_messages(data.get("messages"), file)
        self.process_user_profile(data.get("profile"), file)
        self.process_users(data.get("users"), file)
        self.process_searches(data.get("searches"), file)
        self.process_undark(data.get("freespace"), file)
        self.process_drp(data.get("sqlparse"), file)
        #self.process_videos(data.get("videos"), report_number, file, os.path.dirname(path), datasource_name)
        self.process_logs(data.get("log"), file)
        self.process_published_videos(data.get("published_videos"), file)

    def initialize(self, context):
        self.context = context
        # Messages attributes
        # self.att_msg_uid = self.utils.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", self.case)
        # self.att_msg_uniqueid = self.utils.create_attribute_type('TIKTOK_MSG_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", self.case)
        # self.att_msg_nickname = self.utils.create_attribute_type('TIKTOK_MSG_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", self.case)
        self.att_msg_created_time = self.utils.create_attribute_type('TIKTOK_MSG_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Created Time")
        self.att_msg_participant_1 = self.utils.create_attribute_type('TIKTOK_MSG_PARTICIPANT_1', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Participant 1")
        self.att_msg_participant_2 = self.utils.create_attribute_type('TIKTOK_MSG_PARTICIPANT_2', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Participant 2")
        self.att_msg_message = self.utils.create_attribute_type('TIKTOK_MSG_MESSAGE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Message")
        self.att_msg_read_status = self.utils.create_attribute_type('TIKTOK_MSG_READ_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Read Status")
        self.att_msg_local_info = self.utils.create_attribute_type('TIKTOK_MSG_LOCAL_INFO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Local Info")
        self.att_msg_sender = self.utils.create_attribute_type('TIKTOK_MSG_SENDER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Sender")
        self.att_msg_type = self.utils.create_attribute_type('TIKTOK_MSG_TYPE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Type")
        self.att_msg_deleted = self.utils.create_attribute_type('TIKTOK_MSG_DELETED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Deleted")
        
        #profile
        self.att_prf_avatar = self.utils.create_attribute_type('TIKTOK_PROFILE_AVATAR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Avatar")
        self.att_prf_account_region = self.utils.create_attribute_type('TIKTOK_PROFILE_REGION', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Region")
        self.att_prf_follower_count = self.utils.create_attribute_type('TIKTOK_PROFILE_FOLLOWER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Followers")
        self.att_prf_following_count = self.utils.create_attribute_type('TIKTOK_PROFILE_FOLLOWING', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Following")
        self.att_prf_gender = self.utils.create_attribute_type('TIKTOK_PROFILE_GENDER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Gender")
        self.att_prf_google_account = self.utils.create_attribute_type('TIKTOK_PROFILE_GOOGLE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Google Account")
        # self.att_prf_is_blocked = self.utils.create_attribute_type('TIKTOK_PROFILE_IS_BLOCKED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE, "Is Blocked", self.case)
        # self.att_prf_is_minor = self.utils.create_attribute_type('TIKTOK_PROFILE_IS_MINOR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE, "Is Minor", self.case)
        self.att_prf_nickname = self.utils.create_attribute_type('TIKTOK_PROFILE_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname")
        self.att_prf_register_time = self.utils.create_attribute_type('TIKTOK_PROFILE_REGISTER_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Register Time")
        self.att_prf_sec_uid = self.utils.create_attribute_type('TIKTOK_PROFILE_SEC_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Sec. UID")
        self.att_prf_short_id = self.utils.create_attribute_type('TIKTOK_PROFILE_SHORT_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Short ID")
        self.att_prf_uid = self.utils.create_attribute_type('TIKTOK_PROFILE_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "UID")
        self.att_prf_unique_id = self.utils.create_attribute_type('TIKTOK_PROFILE_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID")
        self.att_prf_follow_status = self.utils.create_attribute_type('TIKTOK_PROFILE_FOLLOW_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Follow Status")
        self.att_prf_url = self.utils.create_attribute_type('TIKTOK_PROFILE_URL', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Url")

        #seaches
        self.att_searches = self.utils.create_attribute_type('TIKTOK_SEARCH', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Search")

        #undark
        self.att_undark_key = self.utils.create_attribute_type('TIKTOK_UNDARK_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Database")
        self.att_undark_output = self.utils.create_attribute_type('TIKTOK_UNDARK_OUTPUT', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Output")

        #drp
        self.att_drp_key = self.utils.create_attribute_type('TIKTOK_DRP_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Database")
        self.att_drp_type = self.utils.create_attribute_type('TIKTOK_DRP_TYPE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Type")
        self.att_drp_offset = self.utils.create_attribute_type('TIKTOK_DRP_OFFSET', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Offset")
        self.att_drp_length = self.utils.create_attribute_type('TIKTOK_DRP_LENGTH', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Length")
        self.att_drp_unallocated = self.utils.create_attribute_type('TIKTOK_DRP_UNALLOCATED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unallocated")
        self.att_drp_data = self.utils.create_attribute_type('TIKTOK_DRP_DATA', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Data")

        #videos

        self.att_vid_key = self.utils.create_attribute_type('TIKTOK_VIDEO_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Key")
        self.att_vid_last_modified = self.utils.create_attribute_type('TIKTOK_VIDEO_LAST_MODIFIED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Last Modified")

        #published videos

        self.att_publish_vid_created_time = self.utils.create_attribute_type('TIKTOK_PUBLISHED_VIDEOS_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Created TIme")
        self.att_publish_vid_url = self.utils.create_attribute_type('TIKTOK_PUBLISHED_VIDEOS_URL', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Url")



        #logs

        self.att_log_time = self.utils.create_attribute_type('TIKTOK_LOGS_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Time")
        self.att_log_session = self.utils.create_attribute_type('TIKTOK_LOGS_SESSION_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Session ID")
        self.att_log_action = self.utils.create_attribute_type('TIKTOK_LOGS_ACTION', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Action")
        self.att_log_body = self.utils.create_attribute_type('TIKTOK_LOGS_BODY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Body")
        



        # self.attributes = {}
        # self.attributes["log_time"]= self.utils.create_attribute_type('TIKTOK_LOGS_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Time", self.case)
        # # self.attributes["log_time"] 


        # self.attributes["log_time"]
        # Create artifacts
        # self.art_messages = self.utils.create_artifact_type(self.module_name, "TSK_MESSAGE","Messages", self.case)
        self.art_messages = self.utils.create_artifact_type(self.module_name, "TIKTOK_MESSAGES","Messages")
        self.art_user_profile = self.utils.create_artifact_type(self.module_name, "TIKTOK_PROFILE", "Profile")
        self.art_profiles = self.utils.create_artifact_type(self.module_name, "TIKTOK_PROFILES_", "Profiles")
        self.art_searches = self.utils.create_artifact_type(self.module_name, "TIKTOK_SEARCHES","Search")
        self.art_videos = self.utils.create_artifact_type(self.module_name, "TIKTOK_VIDEOS", "Videos")
        self.art_publish_videos = self.utils.create_artifact_type(self.module_name, "TIKTOK_PUBLISHED_VIDEOS", "Published Videos")
        self.art_undark = self.utils.create_artifact_type(self.module_name, "TIKTOK_UNDARK", "Deleted rows (Undark)")
        self.art_drp = self.utils.create_artifact_type(self.module_name, "TIKTOK_DRP", "Deleted rows (SQLite-Deleted-Records-Parser)")
        self.art_logs = self.utils.create_artifact_type(self.module_name, "TIKTOK_LOGS", "Logs")
        

        
    def process_user_profile(self, profile, file):
        
        logging.info("Indexing user profile.")
        
        if not profile:
            return

        try:
            
            art = file.newArtifact(self.art_user_profile.getTypeID())
            attributes = []

            #attributes = ArrayList()
            attributes.append(BlackboardAttribute(self.att_prf_account_region,"aweme_user.xml", profile.get("account_region")))
            attributes.append(BlackboardAttribute(self.att_prf_follower_count, "aweme_user.xml", profile.get("follower_count")))
            attributes.append(BlackboardAttribute(self.att_prf_following_count, "aweme_user.xml", profile.get("following_count")))
            attributes.append(BlackboardAttribute(self.att_prf_google_account, "aweme_user.xml", profile.get("google_account")))
            # attributes.append(BlackboardAttribute(self.att_prf_is_blocked, self.module_name, profile.get("is_blocked")))
            # attributes.append(BlackboardAttribute(self.att_prf_is_minor, self.module_name, profile.get("is_minor")))
            attributes.append(BlackboardAttribute(self.att_prf_nickname, "aweme_user.xml", profile.get("nickname")))
            attributes.append(BlackboardAttribute(self.att_prf_register_time, "aweme_user.xml", profile.get("register_time")))
            attributes.append(BlackboardAttribute(self.att_prf_sec_uid, "aweme_user.xml", profile.get("sec_uid")))
            attributes.append(BlackboardAttribute(self.att_prf_short_id, "aweme_user.xml", profile.get("short_id")))
            attributes.append(BlackboardAttribute(self.att_prf_uid, "aweme_user.xml", profile.get("uid")))
            attributes.append(BlackboardAttribute(self.att_prf_unique_id, "aweme_user.xml", profile.get("unique_id")))
        
            art.addAttributes(attributes)
            self.utils.index_artifact(art, self.art_user_profile)        
        except Exception as e:
            logging.warning("Error getting user profile: " + str(e))

    def process_messages(self, conversations, file):
        logging.info("Indexing user messages")
        if not conversations:
            return

        for c in conversations:
            
            participant_1 = c.get("participant_1")
            participant_2 = c.get("participant_2")

            account = self.utils.add_account_type("Tiktok", "Tiktok")
            contact_1 = self.utils.get_or_create_account(account, file, participant_1)
            contact_2 = self.utils.get_or_create_account(account, file, participant_2)
                
            
            for m in c.get("messages"):
                try:    
                    # art = file.newArtifact(self.art_messages.getTypeID())
                    art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_MESSAGE)


                    
                    
                    # attributes.append(BlackboardAttribute(self.att_msg_participant_1, self.module_name, participant_1))
                    # attributes.append(BlackboardAttribute(self.att_msg_participant_2, self.module_name, participant_2))
                    # attributes.append(BlackboardAttribute(self.att_msg_sender, "db_im_xx", m.get("sender")))
                    # attributes.append(BlackboardAttribute(self.att_msg_created_time, self.module_name, m.get("createdtime")))
                    
                    art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_FROM, "{}_im.db".format(self.uid), m.get("sender")))
                    art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SUBJECT, "{}_im.db".format(self.uid), m.get("type")))
                    # attributes.append(BlackboardAttribute(self.att_msg_message, self.module_name, m.get("message")))
                    art.addAttribute(BlackboardAttribute(self.att_msg_read_status, "{}_im.db".format(self.uid), m.get("readstatus")))
                    art.addAttribute(BlackboardAttribute(self.att_msg_local_info, "{}_im.db".format(self.uid), m.get("localinfo")))
                    art.addAttribute(BlackboardAttribute(self.att_msg_deleted, "{}_im.db".format(self.uid), m.get("deleted")))
                    art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_TEXT, "{}_im.db".format(self.uid), m.get("message")))
                    art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, "{}_im.db".format(self.uid), m.get("createdtime")))

                    if m.get("sender") == participant_1:
                        art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_TO, "{}_im.db".format(self.uid), participant_2))
                        self.utils.add_relationship(contact_2, [contact_1], art, Relationship.Type.MESSAGE, m.get("createdtime"))
                    else:
                        art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_TO, "{}_im.db".format(self.uid), participant_1))
                        self.utils.add_relationship(contact_1, [contact_2], art, Relationship.Type.MESSAGE, m.get("createdtime"))

                    
                    # self.utils.index_artifact(self.case.getBlackboard(), art, self.art_messages)
                    self.utils.index_artifact(art, BlackboardArtifact.ARTIFACT_TYPE.TSK_MESSAGE)

                except Exception as e:
                    logging.warning("Error getting a message: " + str(e))


    def process_searches(self, searches, file):
        logging.info("Indexing user searches.")
        if not searches:
            return

        for s in searches:
            try: 
                art = file.newArtifact(self.art_searches.getTypeID())
                # art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_EXTRACTED_TEXT)
                
                attributes = []
                attributes.append(BlackboardAttribute(self.att_searches, "search.xml", s))
                art.addAttributes(attributes)
                self.utils.index_artifact(art, self.art_searches)        
            except Exception as e:
                logging.warning("Error getting a search entry: " + str(e))

    def process_undark(self, undarks, file):
        logging.info("Indexing undark output.")
        if not undarks:
            return
        for database, deleted_rows in undarks.items():
            for row in deleted_rows:
                try: 
                    art = file.newArtifact(self.art_undark.getTypeID())
                    attributes = []
                    attributes.append(BlackboardAttribute(self.att_undark_key, database, database))
                    attributes.append(BlackboardAttribute(self.att_undark_output, database, row))
                    art.addAttributes(attributes)
                    self.utils.index_artifact(art, self.art_undark)        
                except Exception as e:
                    logging.warning("Error indexing undark output: " + str(e))

    def process_drp(self, drps, file):
        logging.info("Indexing drp output.")
        if not drps:
            return
        for database, deleted_rows in drps.items():
            for row in deleted_rows:
                try: 
                    art = file.newArtifact(self.art_drp.getTypeID())
                    attributes = []
                    attributes.append(BlackboardAttribute(self.att_drp_key, database, database))
                    attributes.append(BlackboardAttribute(self.att_drp_type, database, row.get("type")))
                    attributes.append(BlackboardAttribute(self.att_drp_offset, database, row.get("offset")))
                    attributes.append(BlackboardAttribute(self.att_drp_length, database, row.get("length")))
                    attributes.append(BlackboardAttribute(self.att_drp_unallocated, database, row.get("unallocated")))
                    attributes.append(BlackboardAttribute(self.att_drp_data, database, row.get("data")))

                    art.addAttributes(attributes)
                    self.utils.index_artifact(art, self.art_drp) 
                except Exception as e:
                    logging.warning("Error indexing drp output: " + str(e))

    def process_users(self, users, file):
        logging.info("Indexing user profiles.")

        if not users:
            return

        for u in users.values():
            try: 
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_CONTACT)
                attributes = []
                attributes.append(BlackboardAttribute(self.att_prf_uid, "db_im_xx", u.get("uid")))
                attributes.append(BlackboardAttribute(self.att_prf_unique_id, "db_im_xx", u.get("uniqueid")))
                attributes.append(BlackboardAttribute(self.att_prf_nickname, "db_im_xx", u.get("nickname")))
                attributes.append(BlackboardAttribute(self.att_prf_avatar, "db_im_xx", u.get("avatar")))
                attributes.append(BlackboardAttribute(self.att_prf_follow_status, "db_im_xx", u.get("follow_status")))
                attributes.append(BlackboardAttribute(self.att_prf_url, "db_im_xx", u.get("url")))

                # self.utils.get_or_create_account(self.comm_manager, file, u.get("uniqueid"))

                art.addAttributes(attributes)
                
                self.utils.index_artifact(art, self.art_profiles)        
            except Exception as e:
                logging.warning("Error getting user: " + str(e))
    
    def process_videos(self, videos, report_number, file, base_path, datasource_name):
        logging.info("Indexing videos.")

        for v in videos:
            try: 
                art = file.newArtifact(self.art_videos.getTypeID())
                attributes = []
                attributes.append(BlackboardAttribute(self.att_vid_key, v.get("key"), v.get("key")))
                attributes.append(BlackboardAttribute(self.att_vid_last_modified, v.get("key"), v.get("last_modified")))
                art.addAttributes(attributes)
                self.utils.index_artifact(art, self.art_videos)        
            except Exception as e:
                logging.warning("Error getting a video: " + str(e))

        path = os.path.join(base_path, "Contents", "internal", "cache", "cache")
        try:
            files = os.listdir(path)
        except:
            logging.warning("Report doesn't have video files.")
            return
        
        for v in files:
            os.rename(os.path.join(path, v), os.path.join(path, v) + ".mp4")

        self.utils.add_to_fileset("{}_Videos".format(datasource_name), [path])

    def process_published_videos(self, videos,file):
        logging.info("Indexing published videos.")
        for v in videos:
            try: 
                art = file.newArtifact(self.art_publish_videos.getTypeID())
                attributes = []
                attributes.append(BlackboardAttribute(self.att_publish_vid_url, "aweme_publish", v.get("video")))
                attributes.append(BlackboardAttribute(self.att_publish_vid_created_time, "aweme_publish", v.get("created_time")))
                art.addAttributes(attributes)
                self.utils.index_artifact(art, self.art_publish_videos)        
            except Exception as e:
                logging.warning("Error getting a video: " + str(e))

    def process_logs(self, logs, file):
        logging.info("Indexing user logs")
        if not logs:
            return

        for l in logs:
            try: 
                art = file.newArtifact(self.art_logs.getTypeID())
                attributes = []
                attributes.append(BlackboardAttribute(self.att_log_action, self.module_name, l.get("action")))
                attributes.append(BlackboardAttribute(self.att_log_time, self.module_name, l.get("time")))
                attributes.append(BlackboardAttribute(self.att_log_session, self.module_name, l.get("session_id")))
                attributes.append(BlackboardAttribute(self.att_log_body, self.module_name, str(l.get("body"))))
            
                art.addAttributes(attributes)
                self.utils.index_artifact(art, self.art_logs)        
            except Exception as e:
                logging.warning("Error getting log: " + str(e))