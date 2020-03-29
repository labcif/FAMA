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

    # TODO: Update this for your UI
    def checkBoxEvent(self, event):
        if self.Exec_Program_CB.isSelected():
            #self.local_settings.setSetting('Exec_Prog_Flag', 'true')
            self.Program_Executable_TF.setEnabled(True)
            self.Find_Program_Exec_BTN.setEnabled(True)
        else:
            #self.local_settings.setSetting('Exec_Prog_Flag', 'false')
            self.Program_Executable_TF.setText("")
            self.Program_Executable_TF.setEnabled(False)
            self.Find_Program_Exec_BTN.setEnabled(False)

        if self.Imp_File_CB.isSelected():
            #self.local_settings.setSetting('Imp_File_Flag', 'true')
            self.File_Imp_TF.setEnabled(True)
            self.Find_Imp_File_BTN.setEnabled(True)
        else:
            #self.local_settings.setSetting('Imp_File_Flag', 'false')
            self.File_Imp_TF.setText("")
            #self.local_settings.setSetting('File_Imp_TF', "")
            self.File_Imp_TF.setEnabled(False)
            self.Find_Imp_File_BTN.setEnabled(False)

    #def keyPressed(self, event):
        #self.local_settings.setSetting('Area', self.area.getText()) 

    #def onchange_cb(self, event):
        #self.local_settings.setSetting('ComboBox', event.item) 
        #self.Error_Message.setText(event.item)

    def onchange_lb(self, event):
        #self.local_settings.setSetting('ListBox', "")
        list_selected = self.List_Box_LB.getSelectedValuesList()
        #self.local_settings.setSetting('ListBox', str(list_selected))      
        # if (len(list_selected) > 0):
            # self.Error_Message.setText(str(list_selected))
        # else:
            # self.Error_Message.setText("")

    def initComponents(self):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))

        self.Label_1 = JLabel("Package ID to be analyzed")
        #self.panel0.add(self.Label_1)
        self.Label_1.setBounds(120,20,60,20)
        self.add(self.Label_1)

        self.Program_Executable_TF = JTextField('com.zhiliaoapp.musically', 25)
        #self.panel0.add(self.Program_Executable_TF)
        self.add(self.Program_Executable_TF)


        self.adb = JCheckBox("Extract data from ADB and analyze it")
        #self.panel0.add(self.adb)
        self.add(self.adb)

        self.jsonReports = JCheckBox("Include old JSON reports")
        #self.panel0.add(self.jsonReports)
        self.add(self.jsonReports)

    def onClick(self, e):

       chooseFile = JFileChooser()
       filter = FileNameExtensionFilter("SQLite", ["sqlite"])
       chooseFile.addChoosableFileFilter(filter)

       ret = chooseFile.showDialog(self.panel0, "Select SQLite")

       if ret == JFileChooser.APPROVE_OPTION:
           file = chooseFile.getSelectedFile()
           Canonical_file = file.getCanonicalPath()
           #text = self.readPath(file)
           if self.File_Imp_TF.isEnabled():
              self.File_Imp_TF.setText(Canonical_file)
              #self.local_settings.setSetting('File_Imp_TF', Canonical_file)
           else:
              #self.local_settings.setSetting('ExecFile', Canonical_file)
              self.Program_Executable_TF.setText(Canonical_file)

    def customizeComponents(self):
        pass
        #self.Exec_Program_CB.setSelected(self.local_settings.getSetting('Exec_Prog_Flag') == 'true')
        #self.Imp_File_CB.setSelected(self.local_settings.getSetting('Imp_File_Flag') == 'true')
        #self.Check_Box_CB.setSelected(self.local_settings.getSetting('Check_Box_1') == 'true')

    def getSettings(self):
        return self.local_settings