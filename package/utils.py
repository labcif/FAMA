import os
import sys
import platform
import tarfile
import xml.etree.ElementTree as ET
import datetime
import subprocess
import shutil
import tarfile
import json
import time
import re
import logging
import sys
from package import imghdr
from package import sndhdr

if (sys.version_info>=(3, 0, 0,)):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

from distutils.dir_util import mkpath
from distutils.errors import DistutilsFileError, DistutilsInternalError

class Utils: 
    @staticmethod
    def get_base_path_folder():
        return os.path.dirname((os.path.dirname(__file__)))

    @staticmethod
    def get_platform():
        version = platform.system().lower()
        if version.startswith('java'):
            import java.lang
            version = java.lang.System.getProperty("os.name").lower()
        
        return version

    @staticmethod
    def get_all_packages():
        return Utils.read_json((os.path.join(Utils.get_base_path_folder(), "modules", "packages.json")))

    @staticmethod
    def find_package(app):
        return Utils.get_all_packages().get(app)

    @staticmethod
    def find_app_name(package):
        for app, pack in Utils.get_all_packages().items():
            if package == pack:
                return app
        
        return None

    @staticmethod
    def generate_tar_gz_file(folder_path, generated_file_path):
        arcname = os.path.basename(generated_file_path).replace('.tar.gz', '')
        with tarfile.open(generated_file_path, mode='w:gz') as archive:
            archive.add(folder_path, recursive=True, arcname = arcname)
    
    @staticmethod
    def list_folders(folder_path):
        folders = []
        if not folder_path or not os.path.exists(folder_path):
            return folders

        for root, directories, files in os.walk(folder_path):
            for directory in directories:
                folders.append(os.path.join(root, directory))

        return folders

    @staticmethod
    def list_files(folder_name, filter_type = None):
        files_list = []
        if not folder_name or not os.path.exists(folder_name):
            return files_list

        for root, _, files in os.walk(os.path.join(Utils.get_base_path_folder(), folder_name)):
            for file in files:
                if filter_type:
                    extension = os.path.splitext(file)[1].strip().lower()
                    if not extension in filter_type:
                        if extension != "": #ignore files with extension
                            continue

                        if not ".db" in filter_type: #we are only checking header for sqlite for now
                            continue
                        
                        #verify sqlite files with extension
                        if not Utils.verify_header_signature(os.path.join(root, file), header_type = b"SQLite", offset = 0):
                            continue

                files_list.append(os.path.join(root, file))
        
        return files_list
    
    @staticmethod
    def get_current_time():
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def get_current_millis():
        return int(round(time.time() * 1000))
    
    @staticmethod
    def safe_members(members): #used to clean : in folders
        for finfo in members:
            if Utils.clean_invalid_filename(finfo.name) == str(finfo.name):
                yield finfo

    @staticmethod
    def clean_invalid_filename(filename, character = ""):
        return re.sub('[<>:|?*"]', character, filename)

    @staticmethod
    def extract_tar(file, path):
        tar = tarfile.open(file)
        tar.extractall(path, members = Utils.safe_members(tar))
        tar.close()

    @staticmethod
    def verify_header_signature(file, header_type, offset, stream = None):
        header = b""
        if stream:
            header = stream.read(32)
        else:
            try:
                with open(file, "rb") as f:
                    header = f.read(32)
            except Exception as e:
                logging.warning(str(e))

        query = header.find(header_type) #query includes position of header

        return query == offset

    @staticmethod
    def xml_attribute_finder(xml_path, attrib_values = None):
        listing = {}
        if not os.path.exists(xml_path):
            return None
            
        root = ET.parse(xml_path).getroot()
        for child in root:
            if not attrib_values or child.attrib.get("name") in attrib_values: #all values or specific value
                if child.attrib.get("value"):
                    value= child.attrib.get("value")
                else:
                    value = child.text

                try:
                    listing[child.attrib.get("name")] = str(value)
                except: #jython2 fix
                    listing[child.attrib.get("name")] = str(value.encode('utf-8','ignore'))

        return listing

    @staticmethod
    def check_and_generate_folder(path):
        if not os.path.exists(path):
            return os.makedirs(path)

        return True

    @staticmethod
    def replace_slash_platform(path):
        if Utils.get_platform().startswith("windows"):
            return path.replace('/', '\\')
        
        return path.replace('\\', '/')

    @staticmethod
    def get_adb_location():
        if Utils.get_platform().startswith("windows"):
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "windows", "adb.exe")
        elif Utils.get_platform().startswith("darwin"):
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "mac", "adb")
        else:
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "linux", "adb")
    
    @staticmethod
    def get_undark_location():
        if Utils.get_platform().startswith( "windows"):
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "windows", "undark.exe")
        elif Utils.get_platform().startswith("darwin"):
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "mac", "undark")
        else:
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "linux", "undark")

    @staticmethod
    def get_base64_location():
        if Utils.get_platform().startswith("windows"):
            return os.path.join(Utils.get_base_path_folder(), "dependencies", "windows", "base64.exe")
        else:
            return "base64"

    @staticmethod
    def run_undark(db):
        undark = Utils.get_undark_location()
        output = subprocess.Popen([undark,'-i', db, '--freespace'], shell=False, stdout=subprocess.PIPE).stdout.read()
        return output

    @staticmethod
    def remove_folder(folder):
        shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def read_json(path):
        f = open(path, "r")
        contents = json.loads(f.read())
        f.close()
        return contents

    @staticmethod
    def save_report(report_name, contents):
        f = open(report_name, "w")
        f.write(json.dumps(contents, indent=2))
        f.close()
    
    @staticmethod
    def date_parser(date, format):
         #python2 suppport
        date = Utils.compat_py23str(date)
        
       
        try:
            return int(time.mktime(datetime.datetime.strptime(str(date),format).timetuple()))
        except Exception as e:
            logging.warning(e)
            return 0

    #REMOVE IN FUTURE
    @staticmethod
    def compat_py23str(x):
        if sys.version_info > (3, 0):
            return str(x)
        else:
            if isinstance(x, unicode):
                try:
                    return unicode(x).encode("utf-8")
                except UnicodeEncodeError:
                    try:
                        return unicode(x).encode("utf-8")
                    except:
                        return str(x)
            else:
                return str(x)
    
    @staticmethod
    def setup_custom_logger(logfile="module.log"):
        formatting = '[%(asctime)s] %(levelname)s [%(module)s] - %(message)s'

        #FILE HANDLER
        logging.basicConfig(level=logging.DEBUG, format=formatting, filemode='a', filename=logfile)

        #STREAM HANDLER
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(formatting))
        logging.getLogger().addHandler(console)
        
    @staticmethod
    def find_folder_has_folder(path, folder):
        folders = Utils.list_folders(folder)
        final_path = None

        for x in filter(lambda x: path in x, folders):
            if x.endswith(path):
                final_path = x
                break

        return final_path

    @staticmethod
    def set_env():
        env_path = os.path.join(Utils.get_base_path_folder(), '.env')
        if not os.path.exists(env_path):
            return None

        handler = open(env_path, 'r')
        contents = handler.read()
        handler.close()

        for line in contents.splitlines():
            items = line.split('=')
            if not len(items) > 1:
                continue

            os.environ[items[0].strip()] = '='.join(items[1:]).strip()

    @staticmethod
    def get_media_type(filepath):
        images_types = [".apng", ".bmp", ".gif", ".ico", ".cur", ".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp", ".png", ".svg", ".tif", ".tiff", ".webp"]
        videos_types = [".webm", ".mkv", ".flv", ".vob", ".ogv", ".drc", ".gifv", ".mng", ".avi", ".mts", ".m2ts", ".ts", ".mov", ".qt", ".wmv", ".yuv", ".rmvb", ".asf", ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".flv", ".f4v"]
        audios_types = [".aa", ".aac", ".aax", ".act", ".aiff", ".alac", ".amr", ".ape", ".au", ".awb", ".dct", ".dss", ".dvf", ".flac", ".gsm", ".iklax", ".ivs", ".m4a", ".m4b", ".m4p", ".mmf", ".mp3", ".mpc", ".msv", ".nmf", ".nsf", ".ogg", ".oga", ".mogg", ".opus", ".ra", ".rm", ".raw", ".rf64", ".sln", ".tta", ".voc", ".vox", ".wav", ".wma", ".wv", ".8svx", ".cda"]

        if Utils.is_url(filepath):
            filepath = urlparse(filepath).path.lower()

        for x in images_types:
            if filepath.endswith(x):
                return "image"

        for x in videos_types:
            if filepath.endswith(x):
                return "video"

        for x in audios_types:
            if filepath.endswith(x):
                return "audio"
        
        #We can't check by url, bypass
        if Utils.is_url(filepath):
            return "unknown"

        filetype = imghdr.what(filepath)
        if filetype:
            return "image"

        filetype = sndhdr.what(filepath)
        if filetype:
            return "audio"

        return "video"

    @staticmethod
    def is_url(path):
        return ('http:' in path or 'https:' in path)

    @staticmethod
    def copy_tree(src, dst, preserve_mode=1, preserve_times=1,
              preserve_symlinks=0, update=0, verbose=1, dry_run=0):
        #OVERRIDE FROM DSTUTILS METHOD
        """Copy an entire directory tree 'src' to a new location 'dst'.
        Both 'src' and 'dst' must be directory names.  If 'src' is not a
        directory, raise DistutilsFileError.  If 'dst' does not exist, it is
        created with 'mkpath()'.  The end result of the copy is that every
        file in 'src' is copied to 'dst', and directories under 'src' are
        recursively copied to 'dst'.  Return the list of files that were
        copied or might have been copied, using their output name.  The
        return value is unaffected by 'update' or 'dry_run': it is simply
        the list of all files under 'src', with the names changed to be
        under 'dst'.
        'preserve_mode' and 'preserve_times' are the same as for
        'copy_file'; note that they only apply to regular files, not to
        directories.  If 'preserve_symlinks' is true, symlinks will be
        copied as symlinks (on platforms that support them!); otherwise
        (the default), the destination of the symlink will be copied.
        'update' and 'verbose' are the same as for 'copy_file'.
        """
        from distutils.file_util import copy_file

        if not dry_run and not os.path.isdir(src):
            raise DistutilsFileError(
                "cannot copy tree '%s': not a directory" % src)
        try:
            names = os.listdir(src)
        except OSError as e:
            if dry_run:
                names = []
            else:
                raise DistutilsFileError(
                    "error listing files in '%s': %s" % (src, e.strerror))

        if not dry_run:
            mkpath(dst, verbose=verbose)

        outputs = []

        for n in names:
            src_name = os.path.join(src, n)
            dst_name = os.path.join(dst, n)

            if n.startswith('.nfs'):
                # skip NFS rename files
                continue

            if preserve_symlinks and os.path.islink(src_name):
                link_dest = os.readlink(src_name)
                if verbose >= 1:
                    logging.info("linking %s -> %s", dst_name, link_dest)
                if not dry_run:
                    os.symlink(link_dest, dst_name)
                outputs.append(dst_name)

            elif os.path.isdir(src_name):
                outputs.extend(
                    Utils.copy_tree(src_name, dst_name, preserve_mode,
                            preserve_times, preserve_symlinks, update,
                            verbose=verbose, dry_run=dry_run))
            else:
                try:
                    copy_file(src_name, dst_name, preserve_mode,
                            preserve_times, update, verbose=verbose,
                            dry_run=dry_run)
                    outputs.append(dst_name)
                except:
                    pass

        return outputs