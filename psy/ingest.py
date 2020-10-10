import os
import json
import logging
import time
from shutil import copyfile

from java.util import UUID
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.casemodule import Case

from package.analyzer import Analyzer
from package.extract import Extract
from package.device import DeviceCommunication
from package.utils import Utils
from psy.psyutils import PsyUtils
from psy.extractor import Extractor

class ProjectIngestModule(DataSourceIngestModule):
    def __init__(self, settings):
        #Set logging path to autopsy log
        Utils.setup_custom_logger(os.path.join(Case.getCurrentCase().getLogDirectoryPath(), "autopsy.log.0"))
        
        #Context of the ingest
        self.context = None

        #Module Settings choosed in ingest settings
        self.settings = settings

        #Autopsy utils methods instance 
        self.utils = PsyUtils()

        #Filemanager for this case
        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

        #Initialize output folder path
        self.temp_module_path = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "FAMA")
        Utils.check_and_generate_folder(self.temp_module_path)
    
    #This method runs when we click ok in ingest module selection
    def startUp(self, context):
        #Set the environment context
        self.context = context
        
        #Method selected in settings
        self.method = self.settings.getSetting('method')
        
    def process(self, dataSource, progressBar):
        #Set progressbar to an scale of 100%
        self.progressBar = progressBar
        progressBar.switchToDeterminate(100)

        #Initialize list of possible data sources
        data_sources = []
        
        max_apps = len(Utils.get_all_packages().values())

        #Extract method for adb selected #THIS IS ONLY USED IN <= AUTOPSY 4.16
        if self.method == "method_adb":
            #Get list of selected apps to extract
            self.apps = json.loads(self.settings.getSetting('apps'))

            jobs = max_apps * 3  #extract, analyser, index           
            self.progressJob = ProgressJob(progressBar, jobs)
        
            self.progressJob.next_job("Extracting from ADB")
            logging.info("Starting ADB")

            #Variable used to store all folders for each device
            folders = Extractor(self.apps, DeviceCommunication.list_devices(), self.progressJob, dsprocessor = False).dump_apps()

            # Add one datasource for each device, with the list of the possible folders
            for serial, folders_list in folders.items():
                datasource_name = "ADB_{}_{}".format(serial, int(time.time()))
                self.utils.add_to_fileset(datasource_name, folders_list)
                
                # Add data source to case to be analised
                for case_datasources in Case.getCurrentCase().getDataSources():
                    if case_datasources.getName() == datasource_name:
                        data_sources.append(case_datasources)
                        break

            logging.info("Ending ADB")
        
        # Add the selected files for the datasource (json, dumps or mount case)
        else:
            logging.info("Using Selected Datasource")
            data_sources.append(dataSource)
            
            self.progressJob = ProgressJob(progressBar, max_apps * 2) #indexing and analying
            
        
        # For each data source, we will process it each one
        for source in data_sources:
            self.process_by_datasource(source)

        self.progressJob.next_job("Done")

    def process_by_datasource(self, dataSource):
        #Since we are running ingest for the same datasource, we remove the output folder first but only for the datasource!
        temp_directory = os.path.join(self.temp_module_path, dataSource.getName().replace(":","_"))
        Utils.remove_folder(temp_directory)
        Utils.check_and_generate_folder(self.temp_module_path)

        self.progressJob.change_text("Analyzing Information for {}".format(dataSource.getName()))

        reports_by_app = {}

        #We will find all dumps on the datasource
        internal = "%_internal.tar.gz"
        external = "%_external.tar.gz"
        
        dumps = []
        dumps.extend(self.fileManager.findFiles(dataSource, internal))
        dumps.extend(self.fileManager.findFiles(dataSource, external))
        
        #We found dumps, the datasource is not a mount path
        if dumps:
            #For each dump, we are going to check it
            for base in dumps:
                #Get app id of the dump
                app_id = base.getName().replace('_internal.tar.gz', '').replace('_external.tar.gz','')
                self.progressJob.next_job("Processing report {} ".format(app_id))
                #No reports for this app yet
                if not reports_by_app.get(app_id):
                    reports_by_app[app_id] = []

                #We can have multiple dumps for the same app. this ensure we don't add the same folder twice
                base_path = os.path.dirname(base.getLocalPath())
                if base_path in reports_by_app[app_id]:
                    continue
                
                #Adds the folder to the list of reports by app
                reports_by_app[app_id].append(base_path)

                #Multiple dumps per app, we are going to create the folder based on the number of the reports
                report_folder_path = os.path.join(temp_directory, app_id, str(len(reports_by_app[app_id])))
                Utils.check_and_generate_folder(report_folder_path)

                self.progressJob.change_text("Analyzing Information for {} ({})".format(dataSource.getName(), app_id))

                #We are going to analyze the dumps and generate the report
                analyzer = Analyzer(app_id, base_path, report_folder_path)
                analyzer.generate_report()

                #Generated json report location
                report_location = os.path.join(report_folder_path, "Report.json")

                #Add to reports list
                item = {}
                item["report"] = report_location
                item["file"] = base
                item["app"] = Utils.find_app_name(app_id)
                self.process_report(item, dataSource)
                
        else:
            base_path = None
            base = None
            # Little hack to know datasource real path
            # We only know the real path on files, folders doesn't provide the real path
            # So we are going to search every file
            files = self.fileManager.findFiles(dataSource, "%")
            for x in files:
                #We should add artifacts to a file, so we add it to the logicalfileset as reference
                if not base:
                    base = x

                # Script needs files inside /data/data/
                # We find a file with this path, we got the base path
                if x.getLocalPath() and '/data/data/' in x.getParentPath():
                    # Multiple SO normalization
                    local = Utils.replace_slash_platform(x.getLocalPath())
                    if Utils.get_platform().startswith("windows"):    
                        base_path = local.split("\\data\\data\\")[0]
                    else:
                        base_path = local.split("/data/data/")[0]

                    #Already have the base folder, stop the find
                    break
            
            # If have the base folder
            if base_path:
                # For all supported apps
                for app_id in Utils.get_all_packages().values():
                    # If app data exists in mount
                    if os.path.exists(os.path.join(base_path, "data", "data", app_id)):
                        # Create report folder
                        report_number = 1
                        report_folder_path = os.path.join(temp_directory, app_id, str(report_number)) #report path
                        Utils.check_and_generate_folder(report_folder_path)

                        self.progressJob.next_job("Analyzing Information for {} ({})".format(dataSource.getName(), app_id))

                        # Folder to analyze
                        analyzer = Analyzer(app_id, base_path, report_folder_path)
                        analyzer.generate_report()
                        
                        # Report
                        report_location = os.path.join(report_folder_path, "Report.json")
                        item = {}
                        item["report"] = report_location
                        item["file"] = base
                        item["app"] = Utils.find_app_name(app_id)
                        self.process_report(item, dataSource)


        # Find all json reports generated by the script
        json_reports = self.fileManager.findFiles(dataSource, "%.json")
        
        # Processing all datasource json reports
        for report in json_reports:
            # Get app id of the json report
            

            try:
                info = Utils.read_json(report.getLocalPath())
                app_id = info["header"]["app_id"]
            except:
                continue
            
            self.progressJob.change_text("Processing report {} ".format(app_id))
            # Since we can have multiple json files for multiple apps, we have to track how many reports exists for each app
            if not reports_by_app.get(app_id):
                reports_by_app[app_id] = []

            reports_by_app[app_id].append("")

            # Path for every report
            report_folder_path = os.path.join(temp_directory, app_id, str(len(reports_by_app[app_id])))
            Utils.check_and_generate_folder(report_folder_path)

            # Copy json report to output folder
            report_location = os.path.join(report_folder_path, "Report.json")
            copyfile(report.getLocalPath(), report_location)

            item = {}
            item["report"] = report_location
            item["file"] = report
            item["app"] = Utils.find_app_name(app_id)
            self.process_report(item, dataSource)
                
        # After all reports, post a message to the ingest messages in box.
        return IngestModule.ProcessResult.OK

    def process_report(self, report, dataSource):
        # Initialize the autopsy module for the report
        try:
            m = __import__("modules.autopsy.{}".format(report["app"]), fromlist=[None])
            self.progressJob.next_job("Processing report {} ".format(report["app"]))
        # Oops, we don't have an autopsy module for this app
        # Standalone app can have an module for an app without having an autopsy module for it
        except:
            logging.warning("Autopsy Module not found for {}".format(report["app"]))
            return
        
        #Start autopsy module instance
        self.module_psy = m.ModulePsy(report["app"])
        
        #Initialize possible blackboard menus
        self.module_psy.initialize(self.context)
        
        #Process report and add information
        #### FIX NUMBER OF REPORTS
        self.module_psy.process_report(dataSource.getName(), report["file"], 0, report["report"])
        

class ProgressJob:
    def __init__(self, progressBar, jobs, maxValue=100):
        if jobs < 1: jobs = 1
        if maxValue < 1: maxValue = 1
        
        self.maxValue = maxValue
        self.atualPercent = 0
        self.increment = int(100 / (jobs + 1))
        self.progressBar = progressBar

    def next_job(self, message):
        self.atualPercent += self.increment
        
        if self.atualPercent > self.maxValue:
            self.atualPercent = self.maxValue
        
        self.progressBar.progress(message, self.atualPercent)

    def change_text(self, message):
        self.progressBar.progress(message)
            


        


