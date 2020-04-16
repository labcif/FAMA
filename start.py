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
    folders = []
    

    if args.dump:
        for dump in args.dump:
            dump_path = os.path.join(Utils.get_base_path_folder(), "dumps", dump)
            if os.path.exists(dump_path):
                folders.append(dump_path)
            else:
                logging.warning("Invalid dump name: {}. Ignoring".format(dump))

    if args.path:
        folders.extend(extract.dump_from_path(args.path, args.app))

    if args.adb:
        if '.' in args.app:
            app_id = args.app
        else:
            app_id = Utils.find_package(args.app)

        for serial, folder in extract.dump_from_adb(app_id).items():
            folders.append(folder)
    
    if not args.output:
        args.output = Utils.get_base_path_folder()


    for folder in folders:
        analyzer = Analyzer(args.app, folder, args.output)
        report = analyzer.generate_report()

        if args.html:
            analyzer.generate_html_report(report, args.output)

    logging.info("Done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Forensics Artefacts Analyzer')
    parser.add_argument('app', help='Application or package to be analyzed <tiktok> or <com.zhiliaoapp.musically>')
    parser.add_argument('-d', '--dump', help='Analyze specific(s) dump(s) <20200307_215555 ...>', nargs='+', required = False)
    parser.add_argument('-p', '--path', help='Dump app data in path (mount or folder structure)', required = False)
    parser.add_argument('-o', '--output', help='Report output path folder', required = False)
    parser.add_argument('-a', '--adb', action='store_true', help='Dump app data directly from device with ADB', required = False)
    parser.add_argument('-H', '--html', action='store_true', help='Generate HTML report', required = False)
    args = parser.parse_args()
    
    start(args)