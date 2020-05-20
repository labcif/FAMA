import json

from java.awt import Font
from java.awt import Dimension
from java.awt import BorderLayout
from javax.swing import JPanel
from javax.swing import BoxLayout
from javax.swing import ButtonGroup
from javax.swing import JLabel

from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel

from collections import OrderedDict

from package.utils import Utils
from psy.psyutils import PsyUtils, SettingsUtils

class ProjectIngestSettingsPanel(IngestModuleIngestJobSettingsPanel):
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()
        self.customizeComponents()

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

        self.p_method = SettingsUtils.createPanel()
        self.bg_method = ButtonGroup()

        autopsy_version = PsyUtils.get_autopsy_version()

        if ((autopsy_version["major"] == 4 and autopsy_version["minor"] <= 15) or autopsy_version["major"] < 4):
            self.p_info.add(self.lb_info)
            self.p_info.add(self.lb_info2, BorderLayout.SOUTH)

            self.rb_selectedDatasource = SettingsUtils.createRadioButton("Analyze selected datasource", "method_datasource", self.onMethodChange)
            self.bg_method.add(self.rb_selectedDatasource)
            
            # self.rb_importReportFile = SettingsUtils.createRadioButton("Import previous generated report file","method_importfile" ,self.onMethodChange)
            self.rb_liveExtraction = SettingsUtils.createRadioButton("Live extraction with ADB","method_adb", self.onMethodChange)
            self.rb_selectedDatasource.setSelected(True)

            #self.bg_method.add(self.rb_importReportFile)
            self.bg_method.add(self.rb_liveExtraction)
            
            self.p_method.add(JLabel("Analysis method"))
            self.p_method.add(self.rb_selectedDatasource)
            self.p_method.add(self.rb_liveExtraction)

        else:
            self.p_info.add(SettingsUtils.createInfoLabel("It will analyze the data source with previously selected method and index the forensic artifacts."))

        self.add(self.p_method)

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
        self.method = self.getMethod()
        self.local_settings.setSetting("method", self.method)

        if self.method == "method_adb":
            self.lb_info.setText("This method is used when there is no data source but you have the device.")
            self.lb_info2.setText("It will extract the content of the selected applications from the device, analyze and index the forensic artifacts.")
            self.toggleCheckboxes(True)
        else:
            self.lb_info.setText("This method is used when the application data has already been collected.")
            self.lb_info2.setText("It will analyze the data source previously added to the data source and index the forensic artifacts.")
            self.toggleCheckboxes(False)
            
        

    def getSettings(self):
        return self.local_settings
    
    def getMethod(self):
        selection = self.bg_method.getSelection()
        if not selection:
            return None

        return selection.getActionCommand()
    
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
