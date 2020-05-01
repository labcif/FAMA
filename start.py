import argparse
import os
import sys
import logging

from package.extract import Extract
from package.analyzer import Analyzer
from package.utils import Utils

#python3 start.py tiktok --path "/Users/Nogueira/Desktop/Projeto/ExemploMount" --adb
#python3 start.py tiktok --dump 20200307_215555 20200307_201252

def start(args):
    Utils.setup_custom_logger()
    logging.info("Starting")
    
    extract = Extract()

    if not args.output:
        args.output = os.path.join(Utils.get_base_path_folder(), "report")

    Utils.remove_folder(args.output) #clean report folder

    for app in args.app:
        folders = []

        if '.' in app:
            app_id = app
        else:
            app_id = Utils.find_package(app)

        if args.dump:
            for dump in args.dump:
                dump_path = os.path.join(Utils.get_base_path_folder(), "dumps", dump)
                if os.path.exists(dump_path):
                    for folder in os.listdir(dump_path):
                        folders.append(os.path.join(dump_path, folder))
                else:
                    logging.warning("Invalid dump name: {}. Ignoring".format(dump))

        if args.path:
            folders.append(args.path)

        if args.adb:
            for serial, folder in extract.dump_from_adb(app_id).items():
                folders.append(folder)
        
        for folder in folders:
            analyzer = Analyzer(app, folder, args.output)
            report = analyzer.generate_report()

            if args.html and report:
                analyzer.generate_html_report(report, os.path.join(args.output, app_id))

    logging.info("Done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Forensics Artefacts Analyzer')
    parser.add_argument('app', help='Application or package to be analyzed <tiktok> or <com.zhiliaoapp.musically>', nargs='+')
    parser.add_argument('-d', '--dump', help='Analyze specific(s) dump(s) <20200307_215555 ...>', nargs='+', required = False)
    parser.add_argument('-p', '--path', help='Dump app data in path (mount or folder structure)', required = False)
    parser.add_argument('-o', '--output', help='Report output path folder', required = False)
    parser.add_argument('-a', '--adb', action='store_true', help='Dump app data directly from device with ADB', required = False)
    parser.add_argument('-H', '--html', action='store_true', help='Generate HTML report', required = False)
    args = parser.parse_args()
    
    start(args)