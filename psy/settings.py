from javax.swing import BoxLayout
from javax.swing import JCheckBox
from javax.swing import JComponent
from javax.swing import JPanel

from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel

#https://github.com/HienTH/autopsy/blob/master/pythonExamples/fileIngestModuleWithGui.py    
class ProjectSettingsPanelSettings(IngestModuleIngestJobSettings):
    serialVersionUID = 1L

    def __init__(self):
        self.flag = False

    def getVersionNumber(self):
        return serialVersionUID

    # TODO: Define getters and settings for data you want to store from UI
    def getFlag(self):
        return self.flag

    def setFlag(self, flag):
        self.flag = flag

class ProjectSettingsPanel(IngestModuleIngestJobSettingsPanel):
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()
        self.customizeComponents()

    # TODO: Update this for your UI
    def checkBoxEvent(self, event):
        if self.checkbox.isSelected():
            self.local_settings.setFlag(True)
        else:
            self.local_settings.setFlag(False)

    def initComponents(self):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))
        self.checkbox = JCheckBox("Flag", actionPerformed=self.checkBoxEvent)
        self.add(self.checkbox)

    def customizeComponents(self):
        self.checkbox.setSelected(self.local_settings.getFlag())

    def getSettings(self):
        return self.local_settings