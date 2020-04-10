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

from utils import Utils

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
        self.local_settings.setSetting('clean_temp', 'true' if self.clean_temp.isSelected() else 'false')
        self.local_settings.setSetting('old_report', 'true' if self.json_reports.isSelected() else 'false')
        self.local_settings.setSetting('app', self.app.getSelectedItem().split(' (')[0].lower())

    def initComponents(self):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))

        self.label = JLabel("Application to be analyzed")
        self.label.setBounds(120,20,60,20)
        self.add(self.label)

        self.combobox_data = []
        for app, app_id in Utils.get_all_packages().items():
            self.combobox_data.append("{} ({})".format(app.capitalize(), app_id))

        self.app = JComboBox(sorted(self.combobox_data), itemStateChanged = self.event)
        self.add(self.app)

        self.adb = JCheckBox("Extract data from ADB and analyze it", actionPerformed=self.event)
        self.add(self.adb)

        self.json_reports = JCheckBox("Include old JSON reports")
        self.add(self.json_reports)

        self.clean_temp = JCheckBox("Clean temporary folder if exists", actionPerformed=self.event)
        self.clean_temp.setSelected(True)
        self.add(self.clean_temp)

    def customizeComponents(self):
        self.app.setSelectedItem("Tiktok (com.zhiliaoapp.musically)")

        self.local_settings.setSetting('adb', 'false')
        self.local_settings.setSetting('clean_temp', 'true')
        self.local_settings.setSetting('old_report', 'false')
        self.local_settings.setSetting('app', self.app.getSelectedItem().split(' (')[0].lower())

    def getSettings(self):
        return self.local_settings