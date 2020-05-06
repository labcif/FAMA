from java.awt import Font
from java.awt import Component
from java.awt import Dimension
from java.awt import BorderLayout
from javax.swing import JPanel
from javax.swing import JCheckBox
from javax.swing import BoxLayout
from javax.swing import ButtonGroup
from javax.swing import JRadioButton
from javax.swing import JLabel
from javax.swing import JTextArea
from javax.swing import JSeparator
from javax.swing import JScrollPane


from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel

import json
from collections import OrderedDict

from package.utils import Utils

#https://github.com/HienTH/autopsy/blob/master/pythonExamples/fileIngestModuleWithGui.py    
class ProjectIngestSettingsPanelSettings(IngestModuleIngestJobSettings):
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

class ProjectIngestSettingsPanel(IngestModuleIngestJobSettingsPanel):
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()
        self.customizeComponents()

    # def event(self, event):
    #     self.local_settings.setSetting('adb', 'true' if self.adb.isSelected() else 'false')
    #     #self.local_settings.setSetting('clean_temp', 'true' if self.clean_temp.isSelected() else 'false')
    #     self.local_settings.setSetting('old_report', 'true' if self.json_reports.isSelected() else 'false')
    #     # self.local_settings.setSetting('app', self.app.getSelectedItem().split(' (')[0].lower())

    def initComponents(self):
        self.apps_checkboxes_list = []

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))
        self.setPreferredSize(Dimension(300,0))
        
        # title 
        self.p_title = SettingsUtils.createPanel()
        
        
        self.lb_title = JLabel("Android Forensics")
        self.lb_title.setFont(self.lb_title.getFont().deriveFont(Font.BOLD, 15))
        self.p_title.add(self.lb_title)
        self.add(self.p_title)
        
        # end of title
        
        
        # info menu
        self.p_info = SettingsUtils.createPanel()
        self.p_info.setPreferredSize(Dimension(300,20))
        
        self.lb_info = SettingsUtils.createInfoLabel("")
        self.lb_info2 = SettingsUtils.createInfoLabel("")
        self.sp2 = SettingsUtils.createSeparators(1)


        self.p_info.add(self.sp2, BorderLayout.SOUTH)
        self.p_info.add(self.lb_info, BorderLayout.SOUTH)
        self.p_info.add(self.lb_info2, BorderLayout.SOUTH)
        
        

        

        # end of info menu

        # method menu

        self.p_method = SettingsUtils.createPanel()
        self.bg_method = ButtonGroup()
        self.rb_selectedDatasource = SettingsUtils.createRadioButton("Analyse selected datasource", "method_datasource", self.onMethodChange)
        self.rb_importReportFile = SettingsUtils.createRadioButton("Import previous generated report file","method_importfile" ,self.onMethodChange)
        self.rb_liveExtraction = SettingsUtils.createRadioButton("Live extraction with ADB","method_adb", self.onMethodChange)
        self.rb_selectedDatasource.setSelected(True)

        self.bg_method.add(self.rb_selectedDatasource)
        self.bg_method.add(self.rb_importReportFile)
        self.bg_method.add(self.rb_liveExtraction)

        self.p_method.add(JLabel("Analysis method"))
        self.p_method.add(self.sp)
        self.p_method.add(self.rb_selectedDatasource)
        self.p_method.add(self.rb_importReportFile)
        self.p_method.add(self.rb_liveExtraction)
        self.add(self.p_method)

        # end of method menu

        #app checkboxes menu
        self.p_apps = SettingsUtils.createPanel(True)
        
        sorted_items = OrderedDict(sorted(Utils.get_all_packages().items()))

        for app, app_id in sorted_items.iteritems():
            #(app, app_id)
            checkbox = SettingsUtils.addApplicationCheckbox(app, app_id, self.getSelectedApps)
            self.add(checkbox)
            self.apps_checkboxes_list.append(checkbox)
            self.p_apps.add(checkbox)
        

        self.add(self.p_apps)
        self.add(self.p_info)
        # end of checkboxes menu

    def customizeComponents(self):
        self.onMethodChange("") #initialize method option
        self.getSelectedApps("") #initialize selected apps
    
    def onMethodChange(self, event):
        self.method = self.bg_method.getSelection().getActionCommand()
        self.local_settings.setSetting("method", self.method)

        if self.method == "method_datasource":
            self.lb_info.setText("This method is used when there is no data source but you have the device.")
            self.lb_info2.setText("It will extract the content of the selected applications from the device, analyze and index the forensic artifacts.")
            self.toggleCheckboxes(False)
            
        elif self.method == "method_importfile":
            self.lb_info.setText("This method is used when you already have a report in json format previously generated by the application.")
            self.lb_info2.setText("It will analyze the report previously added to the data source and index the forensic artifacts.")
            self.toggleCheckboxes(False)
    
        elif self.method == "method_adb":
            self.lb_info.setText("This method is used when the application data has already been collected.")
            self.lb_info2.setText("It will analyze the data source previously added to the data source and index the forensic artifacts.")
            self.toggleCheckboxes(True)

        # self.local_settings.setSetting("apps", self.getSelectedApps())
        
    def getSettings(self):
        return self.local_settings
    
    def getMethod(self):
        return self.bg_method.getSelection().getActionCommand()
    
    def getSelectedApps(self, event):
        selected_apps = []
        
        for cb_app in self.apps_checkboxes_list:
            if cb_app.isSelected():
                selected_apps.append(cb_app.getActionCommand())
        
        self.local_settings.setSetting("apps", json.dumps(selected_apps))
    
    def toggleCheckboxes(self, visible):
        for cb_app in self.apps_checkboxes_list:
            cb_app.setVisible(visible)

class ProjectReportSettingsPanel(JPanel):
    def __init__(self):
        pass

class SettingsUtils:
    @staticmethod
    def createPanel(scroll =False):
        
        panel = JPanel()
        panel.setLayout(BoxLayout(panel, BoxLayout.PAGE_AXIS))
        panel.setAlignmentX(Component.LEFT_ALIGNMENT)
        
        # if scroll:
            # scrollpane = JScrollPane(panel)
            # scrollpane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            # scrollpane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_NEVER)
            # return JPanel().add(scrollpane)
        
        return panel

    @staticmethod
    def addApplicationCheckbox(app, app_id, ap):
        checkbox = JCheckBox("{} ({})".format(app.capitalize(), app_id), actionPerformed= ap)
        checkbox.setActionCommand(app)
        checkbox.setSelected(True)
        checkbox.setVisible(False)
        checkbox.setActionCommand(app_id)
        return checkbox

    @staticmethod
    def createRadioButton(name, ac, ap):
        button = JRadioButton(name, actionPerformed= ap)
        button.setActionCommand(ac)
        return button
    @staticmethod
    def createInfoLabel(text):
        textArea = JTextArea()
        textArea.setLineWrap(True)
        textArea.setWrapStyleWord(True)
        textArea.setOpaque(False)
        textArea.setEditable(False)
        return textArea

    @staticmethod
    def createSeparators(count):
        lines =""
        for i in range(count):
            lines+="<br>"

        return SettingsUtils.createInfoLabel(lines)