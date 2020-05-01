import os
import json
import logging
from shutil import copyfile
from distutils.dir_util import copy_tree

from java.util import UUID
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.casemodule import Case

from package.analyzer import Analyzer
from package.extract import Extract
from package.utils import Utils
from psy.psyutils import PsyUtils

class ProjectIngestModule(DataSourceIngestModule):
    def __init__(self, settings):
        logfile = os.path.join(Case.getCurrentCase().getLogDirectoryPath(), "autopsy.log.0")
        Utils.setup_custom_logger(logfile)
        
        self.context = None
        self.settings = settings
        self.utils = PsyUtils()

        

        
        
        
        # #TODO for each para percorrer as apps e encontrar os packages
        # self.apps_ids =[]
        # for app in self.apps:
        #     if app == None:
        #         continue

        #     self.apps_ids.append(Utils.find_package(app))

        # self.apps_ids = Utils.find_package(self.settings.getSetting('apps'))
        
        #ABORTAR TO DO IN AUTOPSY
        # if not self.apps_ids:
        #     logging.critical("Module not found for {}".format(self.app_id))
        #     self.utils.post_message("Module not found for {}".format(self.app_id))
        #     return None
        logfile = os.path.join(Case.getCurrentCase().getLogDirectoryPath(), "autopsy.log.0")
        Utils.setup_custom_logger(logfile)

        

        
        
        
        

    def startUp(self, context):
        self.context = context
        self.fileManager = Case.getCurrentCase().getServices().getFileManager()
        

        self.method = self.settings.getSetting('method')
        self.apps = self.settings.getSetting('apps')
        self.apps =self.apps.split(";")
    
        logging.info("APPSSS:::: "+ str(self.apps))
        logging.info("METHOD::::::{}".format(self.method))

        # for app in self.apps:
        #     m = __import__("modules.autopsy.{}".format(app), fromlist=[None])  
        #     self.module_psy = m.ModulePsy(app)
        #     self.module_psy.initialize(context)
        #     self.temp_module_path = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics", app)
        #     Utils.remove_folder(self.temp_module_path)
        #     Utils.check_and_generate_folder(self.temp_module_path)
            # self.tempDirectory = os.path.join(self.temp_module_path, self.app_id)
        
        
        
    def process(self, dataSource, progressBar):
        progressBar.switchToDeterminate(100)

        data_sources = [dataSource]

        if self.method == "method_adb":
            progressBar.progress("Extracting from ADB", 0)
            logging.info("Starting ADB")

            for app_id in self.apps:
                if app_id == None:
                    continue

                extract = Extract()
                folders = extract.dump_from_adb(app_id)

                for serial, folder in folders.items():
                    datasource_name = dataSource.getName() + "_ADB_{}".format(serial)
                    self.utils.add_to_fileset(datasource_name, [folder], device_id = UUID.fromString(dataSource.getDeviceId()))

                    for case in Case.getCurrentCase().getDataSources():
                        if case.getName() == datasource_name:
                            data_sources.append(case)
                            break
                logging.info("{} extracted".format(app_id))

                count = 0
                for source in data_sources:
                    count += 1
                    percent = int(count / float(len(data_sources) + 1) * 100)

                    # self.app_id = app_id
                    self.temp_module_path = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics", Utils.find_app_name(app_id))
                    tempDirectory = os.path.join(self.temp_module_path, app_id)
                    self.process_by_datasource(source, progressBar, percent, tempDirectory, app_id)
            
            logging.info("Ending ADB")
            
            
            # TODO FIND ALL APPS APPS PRESENT AT DUMPS AND REPALCE WITH FOR EACH AND APP_ID
             
        app_id = "com.zhiliaoapp.musically"
        self.temp_module_path = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics", Utils.find_app_name(app_id))
        tempDirectory = os.path.join(self.temp_module_path, app_id)
        Utils.remove_folder(tempDirectory)
        
        # Normal ingest
        count = 0
        for source in data_sources:
            count += 1
            percent = int(count / float(len(data_sources) + 1) * 100)
            self.process_by_datasource(source, progressBar, percent, tempDirectory, app_id)
        
        progressBar.progress("Done", 100)

    def process_by_datasource(self, dataSource, progressBar, percent, tempDirectory, app_id):
        logging.critical(str(dataSource.getRootDirectory()))

        internal = app_id + "_internal.tar.gz"
        external = app_id + "_external.tar.gz"
        json_report = "%.json"
        
        Utils.check_and_generate_folder(tempDirectory)

        number_of_reports = len(os.listdir(tempDirectory))

        dumps = []
        dumps.extend(self.fileManager.findFiles(dataSource, internal))
        dumps.extend(self.fileManager.findFiles(dataSource, external))

        json_reports = self.fileManager.findFiles(dataSource, json_report)

        base_paths = []
        reports = []

        progressBar.progress("Analyzing Information for {}".format(dataSource.getName()), percent)
        # Analyse and generate and processing reports 
        if dumps:
            for base in dumps:
                base_path = os.path.dirname(base.getLocalPath())
                if base_path in base_paths:
                    continue

                base_paths.append(base_path)

                number_of_reports+=1
                report_folder_path = os.path.join(tempDirectory,str(number_of_reports)) #report path
                copy_tree(base_path, report_folder_path) #copy from dump to report path
                Utils.check_and_generate_folder(report_folder_path)
                
                analyzer = Analyzer(Utils.find_app_name(app_id), report_folder_path, report_folder_path)
                analyzer.generate_report()

                report_location = os.path.join(report_folder_path, "report", "Report.json")

                item = {}
                item["report"] = report_location
                item["file"] = base
                item["app"] = Utils.find_app_name(app_id)
                reports.append(item)
        else:
            #little hack to know datasource real path
            base_path = None
            base = None
            files = self.fileManager.findFiles(dataSource, "%")
            for x in files:
                if x.getLocalPath() and '/data/data/' in x.getParentPath():
                    local = Utils.replace_slash_platform(x.getLocalPath()) #normalize
                    if Utils.get_platform().startswith("windows"):    
                        base_path = local.split("\\data\\data\\")[0]
                    else:
                        base_path = local.split("/data/data/")[0]

                    base = x
                    break
            
            if base_path:
                number_of_reports+=1
                report_folder_path = os.path.join(tempDirectory,str(number_of_reports)) #report path
                #copy_tree(base_path, report_folder_path) #copy from dump to report path
                Utils.check_and_generate_folder(report_folder_path)

                analyzer = Analyzer(Utils.find_app_name(app_id), base_path, report_folder_path)
                analyzer.generate_report()
                
                report_location = os.path.join(report_folder_path, "report", "Report.json")
                item = {}
                item["report"] = report_location
                item["file"] = base
                item["app"] = Utils.find_app_name(app_id)
                reports.append(item)

        if self.method == "method_importfile":
            # Processing datasource json reports
            for report in json_reports:
                number_of_reports+=1
                report_folder_path = os.path.join(tempDirectory, str(number_of_reports), "report")
                Utils.check_and_generate_folder(report_folder_path)

                report_location = os.path.join(report_folder_path, "Report.json")
                copyfile(report.getLocalPath(), report_location)

                item = {}
                item["report"] = report_location
                item["file"] = report
                item["app"] = Utils.find_app_name(app_id)
                reports.append(item)

        progressBar.progress("Processing Data for {}".format(dataSource.getName()), percent)

        for report in reports:

            if report["app"]:
                m = __import__("modules.autopsy.{}".format(report["app"]), fromlist=[None])  
                self.module_psy = m.ModulePsy(report["app"])
                self.module_psy.initialize(self.context)
                self.module_psy.process_report(dataSource.getName(), report["file"], number_of_reports, report["report"])
            
        # After all reports, post a message to the ingest messages in box.
        return IngestModule.ProcessResult.OK

