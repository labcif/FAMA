# Sample module in the public domain. Feel free to use this as a template
# for your modules (and you can remove this header and take complete credit
# and liability)
#
# Contact: Brian Carrier [carrier <at> sleuthkit [dot] org]
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# Simple data source-level ingest module for Autopsy.
# Used as part of Python tutorials from Basis Technology - August 2015
# 
# Looks for files of a given name, opens then in SQLite, queries the DB,
# and makes artifacts

import jarray
import inspect
import os
import json
from java.lang import Class
from java.lang import System
from java.sql  import DriverManager, SQLException
from java.util.logging import Level
from java.util import ArrayList
from java.io import File
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Blackboard



# Factory that defines the name and details of the module and allows Autopsy
# to create instances of the modules that will do the analysis.
class TiktokIngestModuleFactory(IngestModuleFactoryAdapter):

    moduleName = "TikTok"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "TikTok Forensics Analyzer"

    def getModuleVersionNumber(self):
        return "0.0"

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return TiktokIngestModule()


# Data Source-level ingest module.  One gets created per data source.
class TiktokIngestModule(DataSourceIngestModule):

    _logger = Logger.getLogger(TiktokIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self):
        self.context = None
    
    def create_attribute_type(self, att_name, type, att_desc, skCase):
        try:
            skCase.addArtifactAttributeType(att_name, type, att_desc)
        except:
            self.log(Level.INFO, "Error creating attribute type: " + att_desc)
        return skCase.getAttributeType(att_name)
    
    def create_artifact_type(self, art_name, art_desc, skCase):
        try:
            skCase.addBlackboardArtifactType(art_name, "TIKTOK: " + art_desc)
        except:
            self.log(Level.INFO, "Error creating artifact type: " + art_desc)
        art = skCase.getArtifactType(art_name)
        return art
    
    def index_artifact(self, blackboard, artifact, artifact_type):
        try:
            # Index the artifact for keyword search
            blackboard.indexArtifact(artifact)
        except Blackboard.BlackboardException as e:
            self.log(Level.INFO, "Error indexing artifact " +
                     artifact.getDisplayName() + "" +str(e))
        # Fire an event to notify the UI and others that there is a new log artifact
        IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent(TiktokIngestModuleFactory.moduleName,artifact_type, None))

    
    def process_profile(self, profile, file):
        try: 
                self.log(Level.INFO, "Parsing user profile")
                art = file.newArtifact(self.art_user_profile.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_prf_account_region, TiktokIngestModuleFactory.moduleName, profile.get("account_region")))
                attributes.add(BlackboardAttribute(self.att_prf_follower_count, TiktokIngestModuleFactory.moduleName, profile.get("follower_count")))
                attributes.add(BlackboardAttribute(self.att_prf_following_count, TiktokIngestModuleFactory.moduleName, profile.get("following_count")))
                attributes.add(BlackboardAttribute(self.att_prf_google_account, TiktokIngestModuleFactory.moduleName, profile.get("google_account")))
                attributes.add(BlackboardAttribute(self.att_prf_is_blocked, TiktokIngestModuleFactory.moduleName, profile.get("is_blocked")))
                attributes.add(BlackboardAttribute(self.att_prf_is_minor, TiktokIngestModuleFactory.moduleName, profile.get("is_minor")))
                attributes.add(BlackboardAttribute(self.att_prf_nickname, TiktokIngestModuleFactory.moduleName, profile.get("nickname")))
                attributes.add(BlackboardAttribute(self.att_prf_register_time, TiktokIngestModuleFactory.moduleName, profile.get("register_time")))
                attributes.add(BlackboardAttribute(self.att_prf_sec_uid, TiktokIngestModuleFactory.moduleName, profile.get("sec_uid")))
                attributes.add(BlackboardAttribute(self.att_prf_short_id, TiktokIngestModuleFactory.moduleName, profile.get("short_id")))
                attributes.add(BlackboardAttribute(self.att_prf_uid, TiktokIngestModuleFactory.moduleName, profile.get("uid")))
                attributes.add(BlackboardAttribute(self.att_prf_unique_id, TiktokIngestModuleFactory.moduleName, profile.get("unique_id")))
            
                art.addAttributes(attributes)
                self.index_artifact(self.blackboard, art, self.art_messages)        
        except Exception as e:
                self.log(Level.INFO, "Error getting user profile: " + str(e))
        
        
        
        return
    
    def process_messages(self, messages, file):
        for m in messages:
            try: 
                self.log(Level.INFO, "Parsing a new message")
                art = file.newArtifact(self.art_messages.getTypeID())
                attributes = ArrayList()
                attributes.add(BlackboardAttribute(self.att_msg_uid, TiktokIngestModuleFactory.moduleName, m.get("uid")))
                attributes.add(BlackboardAttribute(self.att_msg_uniqueid, TiktokIngestModuleFactory.moduleName, m.get("uniqueid")))
                attributes.add(BlackboardAttribute(self.att_msg_nickname, TiktokIngestModuleFactory.moduleName, m.get("nickname")))
                attributes.add(BlackboardAttribute(self.att_msg_created_time, TiktokIngestModuleFactory.moduleName, m.get("createdtime")))
                attributes.add(BlackboardAttribute(self.att_msg_message, TiktokIngestModuleFactory.moduleName, m.get("message")))
                attributes.add(BlackboardAttribute(self.att_msg_read_status, TiktokIngestModuleFactory.moduleName, m.get("readstatus")))
                attributes.add(BlackboardAttribute(self.att_msg_local_info, TiktokIngestModuleFactory.moduleName, m.get("localinfo")))
            
                art.addAttributes(attributes)
                self.index_artifact(self.blackboard, art, self.art_messages)        
            except Exception as e:
                self.log(Level.INFO, "Error getting a message: " + str(e))



    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/latest/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context

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
        self.att_prf_account_region = self.create_attribute_type('TIKTOK_PROFILE_REGION', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Region", skCase)
        self.att_prf_follower_count = self.create_attribute_type('TIKTOK_PROFILE_FOLLOWER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Followers", skCase)
        self.att_prf_following_count = self.create_attribute_type('TIKTOK_PROFILE_FOLLOWING', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Following", skCase)
        self.att_prf_gender = self.create_attribute_type('TIKTOK_PROFILE_GENDER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Gender", skCase)
        self.att_prf_google_account = self.create_attribute_type('TIKTOK_PROFILE_GOOGLE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Google Account", skCase)
        self.att_prf_is_blocked = self.create_attribute_type('TIKTOK_PROFILE_IS_BLOCKED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG, "Is Blocked", skCase)
        self.att_prf_is_minor = self.create_attribute_type('TIKTOK_PROFILE_IS_MINOR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Is Minor", skCase)
        self.att_prf_nickname = self.create_attribute_type('TIKTOK_PROFILE_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", skCase)
        self.att_prf_register_time = self.create_attribute_type('TIKTOK_PROFILE_REGISTER_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Register Time", skCase)
        self.att_prf_sec_uid = self.create_attribute_type('TIKTOK_PROFILE_SEC_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Sec. UID", skCase)
        self.att_prf_short_id = self.create_attribute_type('TIKTOK_PROFILE_SHORT_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Short ID", skCase)
        self.att_prf_uid = self.create_attribute_type('TIKTOK_PROFILE_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "UID", skCase)
        self.att_prf_unique_id = self.create_attribute_type('TIKTOK_PROFILE_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", skCase)

        # Create artifacts

        # self.art_contacts = self.create_artifact_type("YPA_CONTACTS_" + guid + "_" + username,"User " + username + " - Contacts", skCase)
        
        self.art_messages = self.create_artifact_type("TIKTOK_MESSAGE_" + "UID","User " + "UID" + " - MESSAGES", skCase)

        self.art_user_profile = self.create_artifact_type("TIKTOK_PROFILE_" + "UID","User " + "UID" + " - PROFILE", skCase)
                    
                    

    def process(self, dataSource, progressBar):

        progressBar.switchToIndeterminate()
        self.blackboard = Case.getCurrentCase().getServices().getBlackboard()
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        files = fileManager.findFiles(dataSource, "REPORT_%.json")
        numFiles = len(files)
        progressBar.switchToDeterminate(numFiles)
        fileCount = 0
        
        
        for file in files:

            # Check if the user pressed cancel while we were busy
            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            self.log(Level.INFO, "Processing file: " + file.getName())
            fileCount += 1

            # Save the DB locally in the temp folder. use file id as name to reduce collisions
            lclReportPath = os.path.join(Case.getCurrentCase().getTempDirectory(), str(file.getId()) + ".json")
            ContentUtils.writeToFile(file, File(lclReportPath))

            data ={}        
            try: 
                # open file~
                with open(lclReportPath) as json_file:
                    data = json.load(json_file)

    

            except Exception as e:
            #    error open file
            
                return IngestModule.ProcessResult.OK
            
            # Query the contacts table in the database and get all columns. 
            try:
                # get info
                messages = data["messages"]
                profile = data["profile"]

                self.log(Level.INFO, "TIKTOK PROFILE: "+ profile)
                self.log(Level.INFO, "TIKTOK: {} messages found!".format(len(messages)))

            except Exception as e:
                # error getting info
                return IngestModule.ProcessResult.OK

            self.process_messages(messages, file)
            self.process_profile(profile, file)
            

      
           
             
                
            # Clean up
            # stmt.close()
            # dbConn.close()
            json_file.close()
            # os.remove(lclReportPath)
            

            
        # After all reports, post a message to the ingest messages in box.
        message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
            "TikTok Forensics Analyzer", "Found %d files" % fileCount)
        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK

