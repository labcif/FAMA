import argparse
import os
import sys
import logging

from package.extract import Extract
from package.analyzer import Analyzer
from package.utils import Utils

#python3 start.py tiktok tinder --path "/Users/Nogueira/Desktop/Projeto/ExemploMount" --adb
#python3 start.py tiktok tinder --dump 20200307_215555 20200307_201252

def start(args):
    Utils.setup_custom_logger()
    Utils.set_env()
    
    logging.info("Starting")
    
    extract = Extract()

    #If we don't found an output folder, we use the "report" folder
    if not args.output:
        args.output = os.path.join(Utils.get_base_path_folder(), "report")

    #Remove previous index.html from output folder
    try:
        os.remove(os.path.join(args.output, "index.html"))
    except:
        pass

    #Remove previous assets from output folder
    try:
        Utils.remove_folder(os.path.join(args.output, "assets"))
    except:
        pass
        
    #List of reports for html output
    reports = []

    for app in args.app:
        folders = []
        
        #This logic support both <appname> and <com.app.id>
        #app > appname
        #app_id > com.app.id
        if '.' in app:
            app = Utils.find_app_name(app)
            app_id = app
        else:
            app_id = Utils.find_package(app)
        
        #app_id output folder
        app_report_base = os.path.join(args.output, app_id)

        #We are starting, let's clean report app output folder first!
        Utils.remove_folder(app_report_base)

        if args.dump:
            #For each dump in arguments
            for dump in args.dump:
                dump_path = os.path.join(Utils.get_base_path_folder(), "dumps", dump)

                #If dump path exists
                if os.path.exists(dump_path):
                    
                    #We list everything in folder
                    for folder in os.listdir(dump_path):

                        #We add every subdirectory to analyze (folder by device)
                        if os.path.isdir(os.path.join(dump_path, folder)):
                            folders.append(os.path.join(dump_path, folder))
                        #We found .tar.gz in the base folder, let's add them too, but add it only if don't add it before
                        elif '.tar.gz' in folder and dump_path not in folders:
                            folders.append(dump_path)
                
                #The dump file not found
                else:
                    logging.warning("Invalid dump name: {}. Ignoring".format(dump))

        #We can use an mount path as input
        if args.path:
            folders.append(args.path)

        #We can use adb to extract contents
        if args.adb:
            for serial, folder in extract.dump_from_adb(app_id).items():
                folders.append(folder)
        
        #For each folder previously added
        index = 0

        

        for folder in folders:
            index += 1

            #Every app can have multiple dumps, so we add a folder for each dump
            report_path = os.path.join(app_report_base, str(index))

            #Analyze every folder
            analyzer = Analyzer(app_id, folder, report_path)
            report = analyzer.generate_report()

            if not report:
                index -= 1

            #If we set html report output, generate it
            if args.html and report:
                #Generate individual html report
                analyzer.generate_html_report(report, report_path)
                
                #Add to list to create index
                reports.append(analyzer.generate_report_summary(report, str(index)))
    
    #Generate html index
    if args.html and reports:
        item = {}
        item["reports"] = reports
        analyzer.generate_html_index(item, args.output)

    logging.info("Done")

if __name__ == "__main__":
    #Possible arguments for app
    parser = argparse.ArgumentParser(description='Forensics Artefacts Analyzer')
    parser.add_argument('app', help='Application or package to be analyzed <tiktok> or <com.zhiliaoapp.musically>', nargs='+')
    parser.add_argument('-d', '--dump', help='Analyze specific(s) dump(s) <20200307_215555 ...>', nargs='+', required = False)
    parser.add_argument('-p', '--path', help='Dump app data in path (mount or folder structure)', required = False)
    parser.add_argument('-o', '--output', help='Report output path folder', required = False)
    parser.add_argument('-a', '--adb', action='store_true', help='Dump app data directly from device with ADB', required = False)
    parser.add_argument('-H', '--html', action='store_true', help='Generate HTML report', required = False)
    args = parser.parse_args()
    
    start(args)