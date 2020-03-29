import inspect
import os
import json
from java.io import File
from java.util import ArrayList
from java.util.logging import Level

from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent

class ProjectIngestModule(DataSourceIngestModule):
    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self, settings):
        self.moduleName = "Tiktok"
        self._logger = Logger.getLogger(self.moduleName)
        self.context = None
        self.settings
    
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
        IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent(self.moduleName,artifact_type, None))

    
    
    def precess_profile(self):
        return None
    
    def process_messages(self):
        return None



    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/latest/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context

        skCase = Case.getCurrentCase().getSleuthkitCase()
        

        # Messages attributes
        self.atr_messages = self.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", skCase)
        
        self.att_msg_uid = self.create_attribute_type('TIKTOK_MSG_UID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Uid", skCase)
        self.att_msg_uniqueid = self.create_attribute_type('TIKTOK_MSG_UNIQUE_ID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Unique ID", skCase)
        self.att_msg_nickname = self.create_attribute_type('TIKTOK_MSG_NICKNAME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Nickname", skCase)
        self.att_msg_created_time = self.create_attribute_type('TIKTOK_MSG_CREATED_TIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Created TIme", skCase)
        self.att_msg_message = self.create_attribute_type('TIKTOK_MSG_MESSAGE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Message", skCase)
        self.att_msg_read_status = self.create_attribute_type('TIKTOK_MSG_READ_STATUS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Read Status", skCase)
        self.att_msg_local_info = self.create_attribute_type('TIKTOK_MSG_LOCAL_INFO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Local Info", skCase)
        
        # Create artifacts

        # self.art_contacts = self.create_artifact_type("YPA_CONTACTS_" + guid + "_" + username,"User " + username + " - Contacts", skCase)
        
        self.art_messages = self.create_artifact_type("TIKTOK_MESSAGE_" + "UID","User " + "UID" + " - MESSAGES", skCase)
                    
                    

    def process(self, dataSource, progressBar):

        progressBar.switchToIndeterminate()
        blackboard = Case.getCurrentCase().getServices().getBlackboard()
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
                self.log(Level.INFO, "TIKTOK: {} messages found!".format(len(messages)))

            except Exception as e:
                # error getting info
                return IngestModule.ProcessResult.OK

            # Cycle through each row and create artifacts
            art = None
            for m in messages:
                try: 
                    self.log(Level.INFO, "Parsing a new message")
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
                    self.index_artifact(blackboard, art, self.art_messages)        
                except Exception as e:
                    self.log(Level.INFO, "Error getting a message: " + str(e))
                
            
             
                
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
