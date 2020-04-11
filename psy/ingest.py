import inspect
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from java.util.logging import Level
from java.util import ArrayList
from java.io import File
from java.util import UUID
from org.sleuthkit.datamodel import AbstractFile
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
from shutil import rmtree, copyfile

from distutils.dir_util import copy_tree

from analyzer import Analyzer
from extract import Extract
from utils import Utils

from psy.psyutils import PsyUtils
from psy.progress import ProgressUpdater

class ProjectIngestModule(DataSourceIngestModule):
    moduleName = "TikTok"

    def __init__(self, settings):
        self._logger = Logger.getLogger(self.moduleName)
        self.context = None
        self.settings = settings
        self.utils = PsyUtils()
        
        self.app = self.settings.getSetting('app')
        self.app_id = Utils.find_package(self.settings.getSetting('app'))
        
        #ABORTAR TO DO IN AUTOPSY
        #if not module_file:
        #    print("[Analyzer] Module not found for {}".format(self.app_id))
        #    return None

        m = __import__("modules.autopsy.{}".format(self.app), fromlist=[None])
        self.module_psy = m.ModulePsy(case = Case.getCurrentCase().getSleuthkitCase(), log = self.log)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

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

    def process_messages(self, path, messages, file):
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

    def process_report(self, file, report_number, path):
        # Check if the user pressed cancel while we were busy
        if self.context.isJobCancelled():
            return IngestModule.ProcessResult.OK

        try: 
            data = Utils.read_json(path)
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
        self.log(Level.INFO, " Processing messages")

        self.process_messages(path, messages, file)
        self.process_user_profile(user_profile, file)
        self.process_users(profiles, file)
        self.process_searches(searches, file)
        self.process_undark(unkdark_ouput, file)
        self.process_videos(videos, report_number, file)

    def startUp(self, context):
        self.context = context

        self.app_name = "com.zhiliaoapp.musically"
        self.tempDirectory = os.path.join(Case.getCurrentCase().getTempDirectory(), self.app_name)
        self.blackboard = Case.getCurrentCase().getServices().getBlackboard()
        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

        
        skCase = Case.getCurrentCase().getSleuthkitCase()

        #self.module_psy.initialize()

        # Messages attributes
        self.att_msg_uid = self.utils.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", skCase)
        self.att_msg_uniqueid = self.utils.create_attribute_type('TIKTOK_MSG_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", skCase)
        self.att_msg_nickname = self.utils.create_attribute_type('TIKTOK_MSG_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", skCase)
        self.att_msg_created_time = self.utils.create_attribute_type('TIKTOK_MSG_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Created TIme", skCase)
        self.att_msg_message = self.utils.create_attribute_type('TIKTOK_MSG_MESSAGE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Message", skCase)
        self.att_msg_read_status = self.utils.create_attribute_type('TIKTOK_MSG_READ_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Read Status", skCase)
        self.att_msg_local_info = self.utils.create_attribute_type('TIKTOK_MSG_LOCAL_INFO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Local Info", skCase)
        
        #profile
        self.att_prf_avatar = self.utils.create_attribute_type('TIKTOK_PROFILE_AVATAR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Avatar", skCase)
        self.att_prf_account_region = self.utils.create_attribute_type('TIKTOK_PROFILE_REGION', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Region", skCase)
        self.att_prf_follower_count = self.utils.create_attribute_type('TIKTOK_PROFILE_FOLLOWER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Followers", skCase)
        self.att_prf_following_count = self.utils.create_attribute_type('TIKTOK_PROFILE_FOLLOWING', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Following", skCase)
        self.att_prf_gender = self.utils.create_attribute_type('TIKTOK_PROFILE_GENDER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Gender", skCase)
        self.att_prf_google_account = self.utils.create_attribute_type('TIKTOK_PROFILE_GOOGLE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Google Account", skCase)
        # self.att_prf_is_blocked = self.utils.create_attribute_type('TIKTOK_PROFILE_IS_BLOCKED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE, "Is Blocked", skCase)
        # self.att_prf_is_minor = self.utils.create_attribute_type('TIKTOK_PROFILE_IS_MINOR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE, "Is Minor", skCase)
        self.att_prf_nickname = self.utils.create_attribute_type('TIKTOK_PROFILE_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", skCase)
        self.att_prf_register_time = self.utils.create_attribute_type('TIKTOK_PROFILE_REGISTER_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Register Time", skCase)
        self.att_prf_sec_uid = self.utils.create_attribute_type('TIKTOK_PROFILE_SEC_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Sec. UID", skCase)
        self.att_prf_short_id = self.utils.create_attribute_type('TIKTOK_PROFILE_SHORT_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Short ID", skCase)
        self.att_prf_uid = self.utils.create_attribute_type('TIKTOK_PROFILE_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "UID", skCase)
        self.att_prf_unique_id = self.utils.create_attribute_type('TIKTOK_PROFILE_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", skCase)

        self.att_prf_follow_status = self.utils.create_attribute_type('TIKTOK_PROFILE_FOLLOW_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Follow Status", skCase)

        #seaches
        self.att_searches = self.utils.create_attribute_type('TIKTOK_SEARCH', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Search", skCase)

        #undark
        self.att_undark_key = self.utils.create_attribute_type('TIKTOK_UNDARK_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Database", skCase)
        self.att_undark_output = self.utils.create_attribute_type('TIKTOK_UNDARK_OUTPUT', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Output", skCase)

        #videos

        self.att_vid_key = self.utils.create_attribute_type('TIKTOK_VIDEO_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Key", skCase)
        self.att_vid_last_modified = self.utils.create_attribute_type('TIKTOK_VIDEO_LAST_MODIFIED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Last Modified", skCase)



        # Create artifacts

        #self.art_contacts = self.utils.create_artifact_type("YPA_CONTACTS_" + guid + "_" + username,"User " + username + " - Contacts", skCase)
        
        self.art_messages = self.utils.create_artifact_type("TIKTOK_MESSAGES","MESSAGES", skCase)
        self.art_user_profile = self.utils.create_artifact_type("TIKTOK_PROFILE", "PROFILE", skCase)
        self.art_profiles = self.utils.create_artifact_type("TIKTOK_PROFILES_", "PROFILES", skCase)
        self.art_searches = self.utils.create_artifact_type("TIKTOK_SEARCHES","SEARCHES", skCase)
        self.art_undark = self.utils.create_artifact_type("TIKTOK_UNDARK", "UNDARK", skCase)
        self.art_videos = self.utils.create_artifact_type("TIKTOK_VIDEOS", "VIDEOS", skCase)

        self.art_undark = self.utils.create_artifact_type("TIKTOK_UNDARK_" + "UID", "User " + "UID" + " - UNDARK", skCase)
        

    def process(self, dataSource, progressBar):
        progressBar.switchToDeterminate(100)

        #self.log(Level.INFO, str(dataSource))

        if self.settings.getSetting('adb') == "true":
            progressBar.progress("Extracting from ADB", 25)
            self.log(Level.INFO, "Starting ADB")
            extract = Extract()
            folders = extract.dump_from_adb(self.app)

            for serial, folder in folders.items():
                self.utils.generate_new_fileset("ADBFileSet_{}".format(serial), [folder])
            
            self.log(Level.INFO, "Ending ADB")

        if self.settings.getSetting('clean_temp') == "true":
            self.log(Level.INFO, "Cleaning temp folder") #TODO
            # try:
            #     rmtree(os.path.join(Case.getCurrentCase().getTempDirectory(), app_name))
            # except Exception as e:
            #     self.log(Level.INFO, "REMOVE TEMPORARY FOLDER ERROR" + str(e))
            # os.makedirs(os.path.join(Case.getCurrentCase().getTempDirectory(), app_name))

        fileCount = 0

        internal = self.app_id + "_internal.tar.gz"
        external = self.app_id + "_external.tar.gz"
        json_report = "%.json"
        
        Utils.check_and_generate_folder(self.tempDirectory)

        number_of_reports = len(os.listdir(self.tempDirectory))

        dumps = []
        dumps.extend(self.fileManager.findFiles(dataSource, internal))
        dumps.extend(self.fileManager.findFiles(dataSource, external))

        json_reports = self.fileManager.findFiles(dataSource, json_report)

        base_paths = []
        reports = []

        #for dump in dumps:
        #    base_path = os.path.dirname(dump.getLocalPath())
        #    self.log(Level.INFO, "BASE_PATH" + str(base_path))
        #    if not base_path in base_paths:
        #        base_paths.append(base_path)

        progressBar.progress("Analyzing Information", 50)

        # Analyse and generate and processing reports 
        for base in dumps:
            base_path = os.path.dirname(base.getLocalPath())
            if base_path in base_paths:
                continue

            base_paths.append(base_path)

            number_of_reports+=1
            report_folder_path = os.path.join(self.tempDirectory,str(number_of_reports)) #report path
            copy_tree(base_path, report_folder_path) #copy from dump to report path
            Utils.check_and_generate_folder(report_folder_path)
            
            analyzer = Analyzer(self.app, report_folder_path, report_folder_path)
            analyzer.generate_report()

            report_location = os.path.join(report_folder_path, "report", "Report.json")

            item = {}
            item["report"] = report_location
            item["file"] = base
            reports.append(item)

        # Processing datasource json reports
        for report in json_reports:
            number_of_reports+=1
            report_folder_path = os.path.join(self.tempDirectory, str(number_of_reports), "report")
            Utils.check_and_generate_folder(report_folder_path)

            report_location = os.path.join(report_folder_path, "Report.json")
            copyfile(report.getLocalPath(), report_location)

            item = {}
            item["report"] = report_location
            item["file"] = report
            reports.append(item)

        progressBar.progress("Processing Data", 75)

        for report in reports:
            self.process_report(report["file"], number_of_reports, report["report"])

        progressBar.progress("Done", 100)
            
        # After all reports, post a message to the ingest messages in box.
        message = IngestMessage.createMessage(IngestMessage.MessageType.DATA, "Forensics Analyzer", "Found %d files" % fileCount)
        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK

