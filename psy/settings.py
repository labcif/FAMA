from javax.swing import JCheckBox
from javax.swing import BoxLayout
from javax.swing import JButton
from javax.swing import ButtonGroup
from javax.swing import JComboBox
#from javax.swing import JRadioButton
from javax.swing import JList
from javax.swing import JLabel
from javax.swing import JTextArea
from javax.swing import JTextField
from javax.swing import JLabel
from java.awt import GridLayout
from java.awt import GridBagLayout
from java.awt import GridBagConstraints
from javax.swing import JPanel
from javax.swing import JScrollPane
from javax.swing import JFileChooser
from javax.swing.filechooser import FileNameExtensionFilter

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

    def event(self, event):
        self.local_settings.setSetting('adb', 'true' if self.adb.isSelected() else 'false')
        self.local_settings.setSetting('old_report', 'true' if self.json_reports.isSelected() else 'false')
        self.local_settings.setSetting('app_id', self.app.getText())

    def initComponents(self):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))

        self.label = JLabel("Package ID to be analyzed")
        self.label.setBounds(120,20,60,20)
        self.add(self.label)

        self.app = JTextField('com.zhiliaoapp.musically', 25, focusLost=self.event)
        self.add(self.app)

        self.adb = JCheckBox("Extract data from ADB and analyze it", actionPerformed=self.event)
        self.add(self.adb)

        self.json_reports = JCheckBox("Include old JSON reports")
        self.add(self.json_reports)

    def customizeComponents(self):
        self.local_settings.setSetting('app_id', self.app.getText())

    def getSettings(self):
        return self.local_settings