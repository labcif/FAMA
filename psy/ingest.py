import inspect
import os
import json
from java.util.logging import Level
from java.util import ArrayList
from java.io import File
from java.util import UUID
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from shutil import rmtree

from analyzer import Analyzer
from extract import Extract

from psy.psyutils import PsyUtils
from psy.progress import ProgressUpdater


class ProjectIngestModule(DataSourceIngestModule):
    moduleName = "TikTok"

    def __init__(self, settings):
        self._logger = Logger.getLogger(self.moduleName)
        self.context = None
        self.settings = settings
        self.utils = PsyUtils()

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    
    def create_attribute_type(self, att_name, type, att_desc, skCase):
        try:
            skCase.addArtifactAttributeType(att_name, type, att_desc)
        except:
            self.log(Level.INFO, self.moduleName + " Error creating attribute type: " + att_desc)
        return skCase.getAttributeType(att_name)
    
    def create_artifact_type(self, art_name, art_desc, skCase):
        try:
            skCase.addBlackboardArtifactType(art_name, "TIKTOK: " + art_desc)
        except:
            self.log(Level.INFO, self.moduleName +" Error creating artifact type: " + art_desc)
        art = skCase.getArtifactType(art_name)
        return art
    
    def index_artifact(self, blackboard, artifact, artifact_type):
        try:
            # Index the artifact for keyword search
            blackboard.indexArtifact(artifact)
        except Blackboard.BlackboardException as e:
            self.log(Level.INFO, self.moduleName + " Error indexing artifact " +
                     artifact.getDisplayName() + "" +str(e))
        # Fire an event to notify the UI and others that there is a new log artifact
        IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent(self.moduleName,artifact_type, None))

    
    def process_user_profile(self, profile, file):
        try: 
                self.log(Level.INFO, self.moduleName + " Parsing user profile")
                art = file.newArtifact(self.art_user_profile.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_prf_account_region, self.moduleName, profile.get("account_region")))
                attributes.add(BlackboardAttribute(self.att_prf_follower_count, self.moduleName, profile.get("follower_count")))
                attributes.add(BlackboardAttribute(self.att_prf_following_count, self.moduleName, profile.get("following_count")))
                attributes.add(BlackboardAttribute(self.att_prf_google_account, self.moduleName, profile.get("google_account")))
                # attributes.add(BlackboardAttribute(self.att_prf_is_blocked, self.moduleName, profile.get("is_blocked")))
                # attributes.add(BlackboardAttribute(self.att_prf_is_minor, self.moduleName, profile.get("is_minor")))
                attributes.add(BlackboardAttribute(self.att_prf_nickname, self.moduleName, profile.get("nickname")))
                attributes.add(BlackboardAttribute(self.att_prf_register_time, self.moduleName, profile.get("register_time")))
                attributes.add(BlackboardAttribute(self.att_prf_sec_uid, self.moduleName, profile.get("sec_uid")))
                attributes.add(BlackboardAttribute(self.att_prf_short_id, self.moduleName, profile.get("short_id")))
                attributes.add(BlackboardAttribute(self.att_prf_uid, self.moduleName, profile.get("uid")))
                attributes.add(BlackboardAttribute(self.att_prf_unique_id, self.moduleName, profile.get("unique_id")))
            
                art.addAttributes(attributes)
                self.index_artifact(self.blackboard, art, self.art_user_profile)        
        except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting user profile: " + str(e))
        
      
    
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
                self.index_artifact(self.blackboard, art, self.art_messages)        
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
                self.index_artifact(self.blackboard, art, self.art_searches)        
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
                self.index_artifact(self.blackboard, art, self.art_undark)        
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
                self.index_artifact(self.blackboard, art, self.art_profiles)        
            except Exception as e:
                self.log(Level.INFO, self.moduleName + " Error getting user: " + str(e))




    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/latest/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context

        if self.settings.getSetting('adb') == "true":
            self.log(Level.INFO, "Starting ADB")
            extract = Extract()
            folders = extract.dump_from_adb(self.settings.getSetting('app_id'))

            for serial, folder in folders.items():
                self.utils.generate_new_fileset("ADBFileSet_{}".format(serial), [folder])
            
            self.log(Level.INFO, "Ending ADB")
            
        
        skCase = Case.getCurrentCase().getSleuthkitCase()
        # Messages attributes
        
        self.att_msg_uid = self.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", skCase)
        self.att_msg_uniqueid = self.create_attribute_type('TIKTOK_MSG_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", skCase)
        self.att_msg_nickname = self.create_attribute_type('TIKTOK_MSG_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", skCase)
        self.att_msg_created_time = self.create_attribute_type('TIKTOK_MSG_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Created TIme", skCase)
        self.att_msg_message = self.create_attribute_type('TIKTOK_MSG_MESSAGE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Message", skCase)
        self.att_msg_read_status = self.create_attribute_type('TIKTOK_MSG_READ_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Read Status", skCase)
        self.att_msg_local_info = self.create_attribute_type('TIKTOK_MSG_LOCAL_INFO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Local Info", skCase)
        
        #profile
        self.att_prf_avatar = self.create_attribute_type('TIKTOK_PROFILE_AVATAR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Avatar", skCase)
        self.att_prf_account_region = self.create_attribute_type('TIKTOK_PROFILE_REGION', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Region", skCase)
        self.att_prf_follower_count = self.create_attribute_type('TIKTOK_PROFILE_FOLLOWER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Followers", skCase)
        self.att_prf_following_count = self.create_attribute_type('TIKTOK_PROFILE_FOLLOWING', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Following", skCase)
        self.att_prf_gender = self.create_attribute_type('TIKTOK_PROFILE_GENDER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Gender", skCase)
        self.att_prf_google_account = self.create_attribute_type('TIKTOK_PROFILE_GOOGLE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Google Account", skCase)
        # self.att_prf_is_blocked = self.create_attribute_type('TIKTOK_PROFILE_IS_BLOCKED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE, "Is Blocked", skCase)
        # self.att_prf_is_minor = self.create_attribute_type('TIKTOK_PROFILE_IS_MINOR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE, "Is Minor", skCase)
        self.att_prf_nickname = self.create_attribute_type('TIKTOK_PROFILE_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", skCase)
        self.att_prf_register_time = self.create_attribute_type('TIKTOK_PROFILE_REGISTER_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Register Time", skCase)
        self.att_prf_sec_uid = self.create_attribute_type('TIKTOK_PROFILE_SEC_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Sec. UID", skCase)
        self.att_prf_short_id = self.create_attribute_type('TIKTOK_PROFILE_SHORT_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Short ID", skCase)
        self.att_prf_uid = self.create_attribute_type('TIKTOK_PROFILE_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "UID", skCase)
        self.att_prf_unique_id = self.create_attribute_type('TIKTOK_PROFILE_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", skCase)

        self.att_prf_follow_status = self.create_attribute_type('TIKTOK_PROFILE_FOLLOW_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Follow Status", skCase)

        #seaches
        self.att_searches = self.create_attribute_type('TIKTOK_SEARCH', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Search", skCase)

        #undark
        self.att_undark_key = self.create_attribute_type('TIKTOK_UNDARK_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Database", skCase)
        self.att_undark_output = self.create_attribute_type('TIKTOK_UNDARK_OUTPUT', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Output", skCase)


        # Create artifacts

        # self.art_contacts = self.create_artifact_type("YPA_CONTACTS_" + guid + "_" + username,"User " + username + " - Contacts", skCase)
        
        self.art_messages = self.create_artifact_type("TIKTOK_MESSAGE_" + "UID","User " + "UID" + " - MESSAGES", skCase)
        self.art_user_profile = self.create_artifact_type("TIKTOK_PROFILE_" + "UID","User " + "UID" + " - PROFILE", skCase)
        self.art_profiles = self.create_artifact_type("TIKTOK_PROFILES_" + "UID", "User " + "UID" + " - PROFILES", skCase)
        self.art_searches = self.create_artifact_type("TIKTOK_SEARCHES_" + "UID", "User " + "UID" + " - SEARCHES", skCase)

        self.art_undark = self.create_artifact_type("TIKTOK_UNDARK_" + "UID", "User " + "UID" + " - UNDARK", skCase)
        

    def process(self, dataSource, progressBar):
        #progressBar.progress(5)

        progressBar.switchToIndeterminate()
        self.blackboard = Case.getCurrentCase().getServices().getBlackboard()
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        # files = fileManager.findFiles(dataSource, "Report.json")
        # progressBar.switchToDeterminate(1)
        
        fileCount = 0

        app_name = "com.zhiliaoapp.musically"
        internal = app_name + "_internal.tar.gz"
        external = app_name + "_external.tar.gz"


        try:
            rmtree(os.path.join(Case.getCurrentCase().getTempDirectory(), app_name))
        except:
            pass
        os.makedirs(os.path.join(Case.getCurrentCase().getTempDirectory(), app_name))

        internal_files = fileManager.findFiles(dataSource, internal)
        external_files = fileManager.findFiles(dataSource, external)

        
        lclInternalPath = os.path.join(Case.getCurrentCase().getTempDirectory(),app_name, str(internal_files[0].getName()) + internal)
        lclExternalPath = os.path.join(Case.getCurrentCase().getTempDirectory(),app_name, str(external_files[0].getName()) + external)        

        ContentUtils.writeToFile(external_files[0], File(lclExternalPath))
        ContentUtils.writeToFile(internal_files[0], File(lclInternalPath))

        
        
        analyzer = Analyzer(os.path.join(Case.getCurrentCase().getTempDirectory(),app_name), os.path.join(Case.getCurrentCase().getTempDirectory(),app_name))
        analyzer.generate_report()
        
   
        self.log(Level.INFO,str(os.path.join(Case.getCurrentCase().getTempDirectory(),app_name, "report")))
    
    
        
        
        for file in internal_files:
            
            # Check if the user pressed cancel while we were busy
            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            self.log(Level.INFO, self.moduleName + " Processing file: " + file.getName())
            fileCount += 1

            # Save the DB locally in the temp folder. use file id as name to reduce collisions
            lclReportPath = os.path.join(Case.getCurrentCase().getTempDirectory(), app_name, "report", "Report.json")
            # ContentUtils.writeToFile(file, File(lclReportPath))

            data ={}        
            try: 
                # open file~
                with open(lclReportPath) as json_file:
                    data = json.load(json_file)
            except Exception as e:
                return IngestModule.ProcessResult.OK
            
            # Query the contacts table in the database and get all columns. 
            try:
                # get info
                messages = data["messages"]
                user_profile = data["profile"]
                profiles = data["users"]
                searches = data["searches"]
                unkdark_ouput = data["freespace"]
            except Exception as e:
                message = IngestMessage.createMessage(IngestMessage.MessageType.DATA, "TikTok", "Report file with wrong structure")
                IngestServices.getInstance().postMessage(message)
                return IngestModule.ProcessResult.OK

            self.process_messages(messages, file)
            self.process_user_profile(user_profile, file)
            self.process_users(profiles, file)
            self.process_searches(searches, file)
            self.process_undark(unkdark_ouput, file)
        

        
           
             
                
            # Clean up
            # stmt.close()
            # dbConn.close()
        json_file.close()
            # os.remove(lclReportPath)







        # inicio
        # for file in files:

        #     # Check if the user pressed cancel while we were busy
        #     if self.context.isJobCancelled():
        #         return IngestModule.ProcessResult.OK

        #     self.log(Level.INFO, self.moduleName + " Processing file: " + file.getName())
        #     fileCount += 1

        #     # Save the DB locally in the temp folder. use file id as name to reduce collisions
        #     lclReportPath = os.path.join(Case.getCurrentCase().getTempDirectory(), str(file.getId()) + ".json")
        #     ContentUtils.writeToFile(file, File(lclReportPath))

        #     data ={}        
        #     try: 
        #         # open file~
        #         with open(lclReportPath) as json_file:
        #             data = json.load(json_file)
        #     except Exception as e:
        #         return IngestModule.ProcessResult.OK
            
        #     # Query the contacts table in the database and get all columns. 
        #     try:
        #         # get info
        #         messages = data["messages"]
        #         user_profile = data["profile"]
        #         profiles = data["users"]
        #         searches = data["searches"]
        #         unkdark_ouput = data["freespace"]
        #     except Exception as e:
        #         message = IngestMessage.createMessage(IngestMessage.MessageType.DATA, "TikTok", "Report file with wrong structure")
        #         IngestServices.getInstance().postMessage(message)
        #         return IngestModule.ProcessResult.OK

        #     self.process_messages(messages, file)
        #     self.process_user_profile(user_profile, file)
        #     self.process_users(profiles, file)
        #     self.process_searches(searches, file)
        #     self.process_undark(unkdark_ouput, file)
        # fim

      
           
             
                
        #     # Clean up
        #     # stmt.close()
        #     # dbConn.close()
        #     json_file.close()
        #     # os.remove(lclReportPath)
            

            
        # After all reports, post a message to the ingest messages in box.
        message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
            "TikTok Forensics Analyzer", "Found %d files" % fileCount)
        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK

