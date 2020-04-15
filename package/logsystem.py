import logging
import sys
import platform


class LogSystem():

    def __init__(self, module_name="", logfile="module.log"):
        
        # if autopsy_logger != None:
        #     self.secundary_loggger = autopsy_logger


        self.module_name = module_name.upper()
        
        version = platform.system().lower()
        # java logger logic here #TODO
        if version.startswith('java'):
            return
            
        
        
        file_handler = logging.FileHandler(filename=logfile)
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers = [file_handler, stdout_handler]

        # logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', handlers=handlers)
        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=handlers)

    def info(self, msg):
        logging.info("[{}] {}".format(self.module_name, str(msg)))

    def warning(self, msg):
        logging.warning(str(msg))
    
    def critical(self, msg):
        logging.critical(str(msg))
