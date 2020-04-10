import argparse
import os
import sys

from extract import Extract
from analyzer import Analyzer
from utils import Utils

#python3 start.py tiktok --path "/Users/Nogueira/Desktop/Projeto/ExemploMount" --adb
#python3 start.py tiktok --dump 20200307_215555 20200307_201252

def start(args):    
    extract = Extract()
    folders = []

    if args.dump:
        for dump in args.dump:
            dump_path = os.path.join(Utils.get_base_path_folder(), "dumps", dump)
            if os.path.exists(dump_path):
                folders.append(dump_path)
            else:
                print("[App] Invalid dump name: {}. Ignoring".format(dump))

    if args.path:
        folders.extend(extract.dump_from_path(args.path, args.app))

    if args.adb:
        app_id = Utils.find_package(args.app)
        for serial, folder in extract.dump_from_adb(app_id).items():
            folders.append(folder)
    
    if not args.output:
        args.output = Utils.get_base_path_folder()


    for folder in folders:
        analyzer = Analyzer(args.app, folder, args.output)
        analyzer.generate_report()

    print("[App] Done")

    #old stuff, hardcoded
    '''
    folders = extract.dump_from_adb("com.zhiliaoapp.musically")
    #folders = extract.dump_from_path("/mnt/exemplomount")
    #folders = extract.dump_from_path("/Users/Nogueira/Desktop/Projeto/ExemploMount", "com.zhiliaoapp.musically")
    print(folders)
    '''

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Forensics Artefacts Analyzer')
    parser.add_argument('app', help='Application to be analyzed <tiktok>')
    parser.add_argument('-d', '--dump', help='Analyze specific(s) dump(s) <20200307_215555 ...>', nargs='+', required = False)
    parser.add_argument('-p', '--path', help='Dump app data in path (mount or folder structure)', required = False)
    parser.add_argument('-o', '--output', help='Report output path folder', required = False)
    parser.add_argument('-a', '--adb', action='store_true', help='Dump app data directly from device with ADB', required = False)
    args = parser.parse_args()
    
    start(args)