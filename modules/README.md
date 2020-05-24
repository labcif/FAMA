# How to build an application module

## Getting Started

Open the file `/modules/packages.json` and add a reference to your application. The first element `theapplication` is the name of the module, and the second element is the package id of the Android application.

The `report` folder contains the extraction and report logic and the `autopsy` folder contains the file required to connect the report logic with Autopsy program.

```JSON
{
    "app1": "com.the.app1",
    "theapplication": "com.the.application",
    "app2": "com.the.app2"
}
```

## Create the report module

Inside the `/modules/report` folder, create one `.py` file with the previous app name. Based on the _Getting Started_ example, the filename to be created is _theapplication.py_.

```Python
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
        
        #THIS IS THE LOG FUNCTION
        # TO USE THE LOG FUNCTION, WE ARE USING PYTHON LOGGING PACKAGE:
        # https://github.com/python/cpython/blob/3.8/Lib/logging/__init__.py
        # EXAMPLES:
        #logging.info("this is a info log message")
        #logging.warning("this is a warning log message")
        #logging.critical("this is a critical log message")
        
        logging.info("Module started")
        
        # SPECIFIC REPORT FUNCTIONALITIES. YOU CAN USE TIMELINE, MEDIA OR LOCATION ARTIFACT
        # YOU CAN USE A JSON BASED TIMELINE. IN THIS EXAMPLE WE WILL USE A SINGLE TIMELINE FOR THE ENTIRE MODULE
        self.timeline = Timeline()
        #self.locations = Location()
        #self.media = Media()
        

        #TODO
        #HERE IS SOME CODE THAT YOU CONSIDER NECESSARY TO INITIALIZE THE ANALYSIS MODULE.
        #NOT REQUIRED

        
    
    def generate_report(self):
        #TODO
        #HERE IS THE CALL TO THE FUNCTIONS TO OBTAIN THE APPLICATION DATA.
        #REMEMBER THAT THE FINAL RESULT MUST BE AN OBJECT THAT WILL BE CONVERTED TO JSON
        
        #EXAMPLE:
        # self.report["freespace"] = self.get_info(self.get_undark_db)
        # self.report["profile"] = self.get_info(self.get_user_profile)
        # self.report["messages"] = self.get_info(self.get_user_messages)
        
        # UNDARK SHOULD BE FIRST TO ENSURE WE CAN RECOVER OLD DATA

        # ALWAYS CALL THE get_sorted_timeline FUNCTION TO ENSURE THAT THE TIMELINE IS RIGHT
        # YOU CAN PASS THE ARGUMENT "True" IF YOU WANT THE TIMELINE INVERTED
        
        # self.report["timeline"] = self.timeline.get_sorted_timeline()

        logging.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report


    def get_user_profile(self):
        logging.info("Get User Profile...")
        #TODO
        # EXAMPLE OF HOW TO ACCESS A XML FILE
        # ---------
        # XML FILE CONTENT: <string name="myid"> this is my id </string>
        # --------- 

        # xml_file = os.path.join(self.internal_cache_path, "shared_prefs", "aweme_user.xml")
        # user_profile ={}
        # user_profile["id"] = Utils.xml_attribute_finder(xml_file, "myid")
        # return user_profile
        return


    def get_user_messages(self):
        logging.info("Getting User Messages...")
        #TODO
        
        # EXAMPLE OF HOW TO ACCESS A DATABASE
        # db = os.path.join(self.internal_cache_path, "databases", "db_im_xx")
        # database = Database(db1)
        # messages_from_database = database.execute_query("SELECT sender, receiver, message, time FROM messages_table")
        # messages_list = []   
        # for entry in messages_list:
        #     message={}
        #     message["sender"] = entry[0]
        #     message["receiver"] = entry[1]
        #     message["message"] = entry[2]
        #     message["time"] = entry[3]

        # TO ADD CONTENT TO TIMELINE, WE CALL THE ADD FUNCTION
        # FIRST PARAMETER MUST BE A TIMESTAMP, AND THE SECOND THE CONTENT TO BE ADDED (CAN BE AN OBJECT)

        #     self.timeline.add(message["time"], "Message sent/received!")
        #     messages_list.append(message)
        
        # logging.info("{} messages found".format(len(messages_list)))
        #return messages_list
        return

    def get_undark_db(self):
        logging.info("Getting undark output...")
        # UNDARK ALLOWS YOU TO RECOVER FRAGMENTS OF LOST ROWS FROM DATABASES

        # return Database.get_undark_output(self.databases, self.report_path)
        return
    
```

The python file should contain this structure and implement `generate_report(self)` method. Object `self.report` contains the base data for the report structure. Gathered information should be appended to this variable.

`get_category_example(self)` is an example of how can data be processed in this model.

The `__init__.py` file contains the parent structure of the module. `self.shared_preferences` and `self_databases` contains information about the databases and shared preferences of the application. More shared information can be found on this file.

There are many utilities in this framework which can help you with this process, such `Database` for database queries and `Utils` for package helpers.

## Create the autopsy module (optional)

Inside the `/modules/autopsy` folder, create one `.py` file with the same name of the report file.

```Python
import logging

from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.datamodel import Relationship
from org.sleuthkit.datamodel import Account

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
        logging.info("Indexing user profile.")
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
        #     logging.warning("Error getting user profile: " + str(e))

    def process_messages(self, messages, file):
        logging.info("Indexing user messages")
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
        #         logging.warning("Error getting a message: " + str(e))

    def process_undark(self, undarks, file):
        logging.info("Indexing undark output.")
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
        #             logging.warning("Error indexing undark output: " + str(e))

```

Both artifacts and attributes are initialized in the `initialize(self, context)` method. `process_report` is called to process the previously generated report. This method should call implemented methods in this file which will add the contents to the autopsy browser.