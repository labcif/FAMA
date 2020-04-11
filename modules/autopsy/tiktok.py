import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from java.util.logging import Level
from org.sleuthkit.datamodel import BlackboardAttribute

from database import Database
from utils import Utils
from psy.psyutils import PsyUtils

class ModulePsy:
    def __init__(self, case, log):
        self.log = log
        self.case = case
        self.moduleName = "TEST"
        self.log(Level.INFO, str(__file__))
        self.structure = Utils.read_json(__file__.replace('$py.class','.json').replace('.py','.json'))
    
    def initialize(self):
        for att, value in self.structure["attributes"].items():
            self.structure["attributes"][att]["att"] = PsyUtils.create_attribute_type(att, PsyUtils.blackboard_attribute(value["type"]), value["name"], self.case)

        for art, value in self.structure["artifacts"].items():
            self.structure["artifacts"][art]["art"] = PsyUtils.create_artifact_type(att, value["name"], self.case)

    def process_user_profile(self, profile, file):
        try: 
            self.log(Level.INFO, self.moduleName + " Parsing user profile")
            art = file.newArtifact(self.art_user_profile.getTypeID())
            attributes = []

            #attributes = ArrayList()
            attributes.append(BlackboardAttribute(self.att_prf_account_region, self.moduleName, profile.get("account_region")))
            attributes.append(BlackboardAttribute(self.att_prf_follower_count, self.moduleName, profile.get("follower_count")))
            attributes.append(BlackboardAttribute(self.att_prf_following_count, self.moduleName, profile.get("following_count")))
            attributes.append(BlackboardAttribute(self.att_prf_google_account, self.moduleName, profile.get("google_account")))
            # attributes.append(BlackboardAttribute(self.att_prf_is_blocked, self.moduleName, profile.get("is_blocked")))
            # attributes.append(BlackboardAttribute(self.att_prf_is_minor, self.moduleName, profile.get("is_minor")))
            attributes.append(BlackboardAttribute(self.att_prf_nickname, self.moduleName, profile.get("nickname")))
            attributes.append(BlackboardAttribute(self.att_prf_register_time, self.moduleName, profile.get("register_time")))
            attributes.append(BlackboardAttribute(self.att_prf_sec_uid, self.moduleName, profile.get("sec_uid")))
            attributes.append(BlackboardAttribute(self.att_prf_short_id, self.moduleName, profile.get("short_id")))
            attributes.append(BlackboardAttribute(self.att_prf_uid, self.moduleName, profile.get("uid")))
            attributes.append(BlackboardAttribute(self.att_prf_unique_id, self.moduleName, profile.get("unique_id")))
        
            art.addAttributes(attributes)
            self.utils.index_artifact(self.blackboard, art, self.art_user_profile)        
        except Exception as e:
            self.log(Level.INFO, self.moduleName + " Error getting user profile: " + str(e))

    '''

    

    def process_messages(self, messages, file):
        for m in messages:
            try: 
                self.log(Level.INFO, self.moduleName + " Parsing a new message")
                art = file.newArtifact(self.art_messages.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_msg_uid, self.moduleName, m.get("uid")))
                attributes.add(BlackboardAttribute(self.att_msg_uniqueid, self.moduleName, m.get("uniqueid")))
                attributes.add(BlackboardAttribute(self.att_msg_nickname, self.moduleName, m.get("nickname")))
                attributes.add(BlackboardAttribute(self.att_msg_created_time, self.moduleName, m.get("createdtime")))
                attributes.add(BlackboardAttribute(self.att_msg_message, self.moduleName, m.get("message")))
                attributes.add(BlackboardAttribute(self.att_msg_read_status, self.moduleName, m.get("readstatus")))
                attributes.add(BlackboardAttribute(self.att_msg_local_info, self.moduleName, m.get("localinfo")))
            
                art.addAttributes(attributes)
                self.utils.index_artifact(self.blackboard, art, self.art_messages)        
            except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting a message: " + str(e))


    def process_searches(self, searches, file):
        for s in searches:
            try: 
                self.log(Level.INFO, self.moduleName + " Parsing a new search")
                art = file.newArtifact(self.art_searches.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_searches, self.moduleName, s))
                art.addAttributes(attributes)
                self.utils.index_artifact(self.blackboard, art, self.art_searches)        
            except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting a search entry: " + str(e))

    def process_undark(self, undarks, file):
        for database, row in undarks.items():
            try: 
                self.log(Level.INFO, self.moduleName + " Parsing a new undark entry")
                art = file.newArtifact(self.art_undark.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_undark_key, self.moduleName, database))
                attributes.add(BlackboardAttribute(self.att_undark_output, self.moduleName, row))
                art.addAttributes(attributes)
                self.utils.index_artifact(self.blackboard, art, self.art_undark)        
            except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting a message: " + str(e))
    


    def process_users(self, users, file):
        for u in users:
            try: 
                self.log(Level.INFO, self.moduleName + " Parsing a new user")
                art = file.newArtifact(self.art_profiles.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_msg_uid, self.moduleName, u.get("uid")))
                attributes.add(BlackboardAttribute(self.att_msg_uniqueid, self.moduleName, u.get("uniqueid")))
                attributes.add(BlackboardAttribute(self.att_msg_nickname, self.moduleName, u.get("nickname")))
                attributes.add(BlackboardAttribute(self.att_prf_avatar, self.moduleName, u.get("avatar")))
                attributes.add(BlackboardAttribute(self.att_prf_follow_status, self.moduleName, u.get("follow_status")))
            
                art.addAttributes(attributes)
                self.utils.index_artifact(self.blackboard, art, self.art_profiles)        
            except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting user: " + str(e))
    
    def process_videos(self, videos, report_number ,file):

        for v in videos:
            try: 
                self.log(Level.INFO, self.moduleName + " Parsing a new video")
                art = file.newArtifact(self.art_videos.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_vid_key, self.moduleName, v.get("key")))
                attributes.add(BlackboardAttribute(self.att_vid_last_modified, self.moduleName, v.get("last_modified")))
                art.addAttributes(attributes)
                self.utils.index_artifact(self.blackboard, art, self.art_videos)        
            except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting a video: " + str(e))



        path = os.path.join(self.tempDirectory,str(report_number),"report", "Contents", "internal", "cache", "cache")
        try:
            files = os.listdir(path)
        except:
            self.log(Level.INFO, "Report {} doesn't have video files")
            return
        
        for v in files:
            self.log(Level.INFO, os.path.join(path, v))
            os.rename(os.path.join(path, v), os.path.join(path, v) + ".mp4")

        self.utils.generate_new_fileset("Videos", [path])

    def generate(self):
        pass
        #self.process_messages(messages, file)
        #self.process_user_profile(user_profile, file)
        #self.process_users(profiles, file)
        #self.process_searches(searches, file)
        #self.process_undark(unkdark_ouput, file)
        #self.process_videos(videos, report_number, file)
        #self.att_msg_uid = self.utils.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", skCase)
        #self.art_messages = self.utils.create_artifact_type("TIKTOK_MESSAGES","MESSAGES", skCase)
    '''