from package.utils import Utils
from org.sleuthkit.autopsy.casemodule import Case

from psy.psyutils import PsyUtils

class ModulePsyParent:
    def __init__(self, module_name):
        self.context = None
        self.case = Case.getCurrentCase().getSleuthkitCase()
        self.utils = PsyUtils()
        self.module_name = module_name.upper() + ": "

    def initialize(self, context):
        raise NotImplementedError

    def process_report(self, datasource_name, file, report_number, path):
        raise NotImplementedError
