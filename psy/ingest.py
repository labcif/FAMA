import inspect
import os
import sys
import json
import logging
from shutil import rmtree, copyfile
from distutils.dir_util import copy_tree

from java.util.logging import Level
from java.util import UUID
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case

from package.analyzer import Analyzer
from package.extract import Extract
from package.utils import Utils

from psy.psyutils import PsyUtils
from psy.progress import ProgressUpdater

class ProjectIngestModule(DataSourceIngestModule):
    def __init__(self, settings):
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
        
        logfile = os.path.join(Case.getCurrentCase().getLogDirectoryPath(), "autopsy.log.0")
        Utils.setup_custom_logger(logfile)

        self.module_psy = m.ModulePsy(self.app)

        self.utils.post_message("teste")
        self.utils.post_message(str(os.path.join(Case.getCurrentCase().getLogDirectoryPath(), "autopsy.log.0")))

    def startUp(self, context):
        self.context = context
        self.module_psy.initialize(context)

        self.temp_module_path = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "AndroidForensics")

        Utils.check_and_generate_folder(self.temp_module_path)
        self.tempDirectory = os.path.join(self.temp_module_path, self.app_id)

        self.fileManager = Case.getCurrentCase().getServices().getFileManager()
        
    def process(self, dataSource, progressBar):
        progressBar.switchToDeterminate(100)
        logging.info(str(Case.getCurrentCase().getDataSources()))

        data_sources = [dataSource]

        if self.settings.getSetting('adb') == "true":
            progressBar.progress("Extracting from ADB", 40)
            logging.info("Starting ADB")
            extract = Extract()
            folders = extract.dump_from_adb(self.app_id)

            for serial, folder in folders.items():
                datasource_name = dataSource.getName() + "_ADB_{}".format(serial)
                self.utils.add_to_fileset(datasource_name, [folder], device_id = UUID.fromString(dataSource.getDeviceId()))

                for case in Case.getCurrentCase().getDataSources():
                    if case.getName() == datasource_name:
                        data_sources.append(case)
                        break
            
            logging.info("Ending ADB")

        Utils.remove_folder(self.tempDirectory)

        count = 0
        for source in data_sources:
            count += 1
            #percent = int(count / (len(data_sources) + 1) * 100)
            self.process_by_datasource(source, progressBar)
        
        progressBar.progress("Done", 100)

    def process_by_datasource(self, dataSource, progressBar):
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
        #    logging(Level.INFO, "BASE_PATH" + str(base_path))
        #    if not base_path in base_paths:
        #        base_paths.append(base_path)

        progressBar.progress("Analyzing Information for {}".format(dataSource.getName()), 80)

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

        if self.settings.getSetting('old_report') == "true":
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

        progressBar.progress("Processing Data for {}".format(dataSource.getName()), 80)

        for report in reports:
            self.module_psy.process_report(dataSource.getName(), report["file"], number_of_reports, report["report"])
            
        # After all reports, post a message to the ingest messages in box.
        

        return IngestModule.ProcessResult.OK

