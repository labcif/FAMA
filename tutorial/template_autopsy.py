import sys
import os

from java.util.logging import Level
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.datamodel import Relationship
from org.sleuthkit.datamodel import Account
from org.sleuthkit.autopsy.casemodule import Case

from package.database import Database
from package.utils import Utils
from psy.psyutils import PsyUtils

class ModulePsy:
    def __init__(self):
        self.log = Utils.get_logger()
        self.case = Case.getCurrentCase().getSleuthkitCase()
        self.context = None
        self.module_name = "Tiktok:"
        self.utils = PsyUtils()
        
        


    def process_report(self, datasource_name, file, report_number, path):
        if self.context.isJobCancelled():
            return IngestModule.ProcessResult.OK
        
        #TODO
        # HERE WE CAN CALL THE FUNCTIONS THAT WILL INDEX THE REPORT'S ARTIFACTS
        # 
        # EXAMPLE:
        # data = Utils.read_json(path)
        # self.process_messages(data.get("profile"), file)
        # self.process_user_profile(data.get("messages"), file)
        # self.process_users(data.get("freespace"), file)

    def initialize(self, context):
        self.context = context

        # TODO
        # HERE YOU CAN DEFINE THE ARTIFACTS TO DISPLAY ON THE BLACKBOARD
        # EXAMPLE:
        # self.art_user_profile = self.utils.create_artifact_type(self.module_name, "PROFILE", "Profile")
        # self.art_messages = self.utils.create_artifact_type(self.module_name, "MESSAGES","Messages")
        # self.art_undark = self.utils.create_artifact_type(self.module_name, "UNDARK", "Deleted rows")
        
        #TODO
        # HERE YOU CAN DEFINE THE ATTRIBUTES FOR THE ARTIFACTS
        # EXAMPLE:
        # MESSAGE ATTRIBUTES
        # self.att_msg_person_1 = self.utils.create_attribute_type('MSG_PARTICIPANT_1', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Person 1")
        # self.att_msg_person_2 = self.utils.create_attribute_type('MSG_PARTICIPANT_2', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Person 2")
        # self.att_msg_message = self.utils.create_attribute_type('MSG_MESSAGE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Message")
        
        # PROFILE ATTRIBUTES
        # self.att_prf_id = self.utils.create_attribute_type('PROFILE_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "ID")
        
        # DELETED ROWS (UNDARK) ATTRIBUTES
        # self.att_undark_key = self.utils.create_attribute_type('UNDARK_KEY', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Database")
        # self.att_undark_output = self.utils.create_attribute_type('UNDARK_OUTPUT', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Output")


        
        

        
    def process_user_profile(self, profile, file):
        self.log.info("Indexing user profile.")
        if not profile:
            return

        #TODO
        # HERE YOU CAN ADD THE PROFILE ATTRIBUTES FROM THE REPORT AND INDEX THE ARTIFACT TO THE BLACKBOARD

        # EXAMPLE:
        # try:
        #     art = file.newArtifact(self.art_user_profile.getTypeID())
        #     attributes = []
        #     attributes.append(BlackboardAttribute(self.att_prf_id, "source.xml", profile.get("id")))
        # 
        #     art.addAttributes(attributes)
        #     self.utils.index_artifact(art, self.art_user_profile)        
        # 
        # except Exception as e:
        #     self.log.warning("Error getting user profile: " + str(e))



    def process_messages(self, messages, file):
        self.log.info("Indexing user messages")
        if not messages:
            return

        #TODO
        # HERE YOU CAN ADD MESSAGES ATTRIBUTES FROM THE REPORT AND INDEX THE ARTIFACT TO THE BLACKBOARD
        # IN THIS EXAMPLE WE WILL USE AUTOPSY MESSAGE ARTIFACT
        # 
        # EXAMPLE:
        # for message in messages:
        #     try:
        #   
        #         art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_MESSAGE)
                
        # THIS IS USEFUL FOR THE AUTOPSY COMMUNICATIONS TAB
        #         contact_1 = self.utils.get_or_create_account(Account.Type.MESSAGING_APP, file, message.get("sender"))
        #         contact_2 = self.utils.get_or_create_account(Account.Type.MESSAGING_APP, file, message.get("receiver"))
        # 
        #         art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_FROM, "source.db", message.get("sender")))
        #         art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PHONE_NUMBER_TO, "source.db", message.get("receiver")))
        # 
        # THIS IS USEFUL FOR THE AUTOPSY COMMUNICATIONS TAB
        # 
        #         self.utils.add_relationship(contact_1, [contact_2], art, Relationship.Type.MESSAGE, message.get("time"))
        #         self.utils.index_artifact(art, BlackboardArtifact.ARTIFACT_TYPE.TSK_MESSAGE)
        # 
        #     except Exception as e:
        #         self.log.warning("Error getting a message: " + str(e))




    def process_undark(self, undarks, file):
        self.log.info("Indexing undark output.")
        if not undarks:
            return
        
        #TODO
        # for database, deleted_rows in undarks.items():
        #     for row in deleted_rows:
        #         try: 
        #             art = file.newArtifact(self.art_undark.getTypeID())
        #             attributes = []
        #             attributes.append(BlackboardAttribute(self.att_undark_key, database, database))
        #             attributes.append(BlackboardAttribute(self.att_undark_output, database, row))
        #             art.addAttributes(attributes)
        #             self.utils.index_artifact(art, self.art_undark)        
        #         except Exception as e:
        #             self.log.warning("Error indexing undark output: " + str(e))

    