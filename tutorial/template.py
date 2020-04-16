import sys
import json
import os
import tarfile

from package.database import Database
from package.utils import Utils
from modules.report import ModuleParent

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)
        self.log = Utils.get_logger()
        
        #THIS IS THE LOG FUNCTION
        # TO USE THE LOG FUNCTION, WE ARE USING PYTHON LOGGING PACKAGE:
        # https://github.com/python/cpython/blob/3.8/Lib/logging/__init__.py
        # EXAMPLES:
        #self.log.info("this is a info log message")
        #self.log.warning("this is a warning log message")
        #self.log.critical("this is a critical log message")

        self.log.info("Module started")

        #TODO
        #HERE IS SOME CODE THAT YOU CONSIDER NECESSARY TO INITIALIZE THE ANALYSIS MODULE.
        #NOT REQUIRED

        
    
    def generate_report(self):
        #TODO
        #HERE IS THE CALL TO THE FUNCTIONS TO OBTAIN THE APPLICATION DATA.
        #REMEMBER THAT THE FINAL RESULT MUST BE AN OBJECT THAT WILL BE CONVERTED TO JSON
        
        #EXAMPLE:
        # self.report["profile"] = self.get_user_profile()
        # self.report["messages"] = self.get_user_messages()
        # self.report["freespace"] = self.get_undark_db()

        self.log.info("Report Generated")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report


    def get_user_profile(self):
        self.log.info("Get User Profile...")
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
        self.log.info("Getting User Messages...")
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
        #     messages_list.append(message)
        
        # self.log.info("{} messages found".format(len(messages_list)))
        #return messages_list
        return

    def get_undark_db(self):
        self.log.info("Getting undark output...")
        # UNDARK ALLOWS YOU TO RECOVER FRAGMENTS OF LOST ROWS FROM DATABASES

        # return Database.get_undark_output(self.databases, self.report_path)
        return
    


