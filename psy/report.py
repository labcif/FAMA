import inspect

from java.util.logging import Level
from org.sleuthkit.autopsy.coreutils import Logger

class ReportOutput:
    def __init__(self):
        self._logger = Logger.getLogger("ProjectIngestReport")

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)
    
    def generateReport(self, baseReportDir, progressBar):
        pass