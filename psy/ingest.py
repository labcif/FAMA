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
from org.sleuthkit.autopsy.ingest import DataSourceIngestModuleProgress
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.progress import LoggingProgressIndicator
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
    
    def process_videos(self, videos, report_number ,file):

        for v in videos:
            try: 
                self.log(Level.INFO, self.moduleName + " Parsing a new video")
                art = file.newArtifact(self.art_videos.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_vid_key, self.moduleName, v.get("key")))
                attributes.add(BlackboardAttribute(self.att_vid_last_modified, self.moduleName, v.get("last_modified")))
                art.addAttributes(attributes)
                self.index_artifact(self.blackboard, art, self.art_videos)        
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

    def process_report(self, file, report_number, path):
        # Check if the user pressed cancel while we were busy
        if self.context.isJobCancelled():
            return IngestModule.ProcessResult.OK

        self.log(Level.INFO, self.moduleName + " Processing file: " + file.getName())

        # lclReportPath = os.path.join(Case.getCurrentCase().getTempDirectory(), app_name, "report", "Report.json")

        data ={}        
        try: 
            with open(path) as json_file:
                data = json.load(json_file)
        except Exception as e:
            return IngestModule.ProcessResult.OK
        
        try:
            # get info
            messages = data["messages"]
            user_profile = data["profile"]
            profiles = data["users"]
            searches = data["searches"]
            unkdark_ouput = data["freespace"]
            videos = data["videos"]
        except Exception as e:
            message = IngestMessage.createMessage(IngestMessage.MessageType.DATA, "TikTok", "Report file with wrong structure")
            IngestServices.getInstance().postMessage(message)
            return IngestModule.ProcessResult.OK

        self.process_messages(messages, file)
        self.process_user_profile(user_profile, file)
        self.process_users(profiles, file)
        self.process_searches(searches, file)
        self.process_undark(unkdark_ouput, file)
        self.process_videos(videos, report_number, file)
        json_file.close()



    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/latest/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context
        self.app_name = "com.zhiliaoapp.musically"
        self.tempDirectory = os.path.join(Case.getCurrentCase().getTempDirectory(), self.app_name)
        self.blackboard = Case.getCurrentCase().getServices().getBlackboard()
        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

        
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

        #videos

        self.att_vid_key = self.create_attribute_type('TIKTOK_VIDEO_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Key", skCase)
        self.att_vid_last_modified = self.create_attribute_type('TIKTOK_VIDEO_LAST_MODIFIED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Last Modified", skCase)




        # Create artifacts

        # self.art_contacts = self.create_artifact_type("YPA_CONTACTS_" + guid + "_" + username,"User " + username + " - Contacts", skCase)
        
        self.art_messages = self.create_artifact_type("TIKTOK_MESSAGES","MESSAGES", skCase)
        self.art_user_profile = self.create_artifact_type("TIKTOK_PROFILE", "PROFILE", skCase)
        self.art_profiles = self.create_artifact_type("TIKTOK_PROFILES_", "PROFILES", skCase)
        self.art_searches = self.create_artifact_type("TIKTOK_SEARCHES","SEARCHES", skCase)
        self.art_undark = self.create_artifact_type("TIKTOK_UNDARK", "UNDARK", skCase)
        self.art_videos = self.create_artifact_type("TIKTOK_VIDEOS", "VIDEOS", skCase)

        

    def process(self, dataSource, progressBar):
        progressBar.switchToDeterminate(100)

        if self.settings.getSetting('adb') == "true":
            progressBar.progress("Extracting from ADB", 25)
            self.log(Level.INFO, "Starting ADB")
            extract = Extract()
            folders = extract.dump_from_adb(self.settings.getSetting('app_id'))

            for serial, folder in folders.items():
                self.utils.generate_new_fileset("ADBFileSet_{}".format(serial), [folder])
            
            self.log(Level.INFO, "Ending ADB")


        #progressBar.switchToIndeterminate()
        
        # files = fileManager.findFiles(dataSource, "Report.json")
        # progressBar.switchToDeterminate(1)
        
        fileCount = 0

        
        internal = self.app_name + "_internal.tar.gz"
        external = self.app_name + "_external.tar.gz"
        json_report = "%.json"
        

        # try:
        #     rmtree(os.path.join(Case.getCurrentCase().getTempDirectory(), app_name))
        # except Exception as e:
        #     self.log(Level.INFO, "REMOVE TEMPORARY FOLDER ERROR" + str(e))
        # os.makedirs(os.path.join(Case.getCurrentCase().getTempDirectory(), app_name))

        try:
            os.makedirs(os.path.join(Case.getCurrentCase().getTempDirectory(), self.app_name))
        except Exception as e:
            self.log(Level.INFO, "CREATE TEMPORARY FOLDER ERROR" + str(e))

        
        number_of_reports = len(os.listdir(self.tempDirectory))

        internal_files = self.fileManager.findFiles(dataSource, internal)
        external_files = self.fileManager.findFiles(dataSource, external)
        json_reports = self.fileManager.findFiles(dataSource, json_report)

        # Analyse and generate and processing reports 
        if len(internal_files) > 0 and len(internal_files) > 0:
            number_of_reports+=1
            os.makedirs(os.path.join(self.tempDirectory, str(number_of_reports)))
            lclInternalPath = os.path.join(self.tempDirectory,str(number_of_reports), str(internal_files[0].getName()) + internal)
            lclExternalPath = os.path.join(self.tempDirectory,str(number_of_reports), str(external_files[0].getName()) + external)        
            ContentUtils.writeToFile(external_files[0], File(lclExternalPath))
            ContentUtils.writeToFile(internal_files[0], File(lclInternalPath))
            
            progressBar.progress("Analyzing Information", 50)
            
            analyzer = Analyzer(os.path.join(self.tempDirectory,str(number_of_reports)), os.path.join(self.tempDirectory, str(number_of_reports)))
            analyzer.generate_report()

            lclReportsPath = os.path.join(self.tempDirectory,str(number_of_reports),"report", "Report.json")
            self.process_report(internal_files[0], number_of_reports, lclReportsPath)

        # Processing standalone reports
        for report in json_reports:

            number_of_reports+=1
            os.makedirs(os.path.join(self.tempDirectory, str(number_of_reports), "report"))
            lclReportsPath = os.path.join(self.tempDirectory,str(number_of_reports),"report", "Report.json")
            ContentUtils.writeToFile(report, File(lclReportsPath))
            
            self.process_report(report, number_of_reports, lclReportsPath)

        progressBar.progress("Processing Data", 75)

        

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
            
        progressBar.progress("Done", 100)
            
        # After all reports, post a message to the ingest messages in box.
        message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
            "TikTok Forensics Analyzer", "Found %d files" % fileCount)
        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK

