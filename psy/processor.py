from java.awt import Dimension
from java.awt import BorderLayout
from javax.swing import JPanel
from javax.swing import BoxLayout
from javax.swing import JLabel

from psy.psyutils import SettingsUtils

from collections import OrderedDict

from package.utils import Utils

class DataSourcesPanelSettings(JPanel):
    serialVersionUID = 1L

    def __init__(self):
        self.initComponents()
        self.customizeComponents()
        self.selected_apps = []

    def getVersionNumber(self):
        return serialVersionUID

    def readSettings(self):
        pass

    def validatePanel(self):
        return len(self.selected_apps) != 0

    def initComponents(self):
        self.apps_checkboxes_list = []

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))
        self.setPreferredSize(Dimension(543, 172)) #Max 544x173 https://www.sleuthkit.org/autopsy/docs/api-docs/3.1/interfaceorg_1_1sleuthkit_1_1autopsy_1_1corecomponentinterfaces_1_1_data_source_processor.html#a068919818c017ee953180cc79cc68c80
        
        # info menu
        self.p_info = SettingsUtils.createPanel()
        self.p_info.setPreferredSize(Dimension(300,20))
        
        self.lb_info = SettingsUtils.createInfoLabel("This method is used when the application data has already been collected.")
        self.lb_info2 = SettingsUtils.createInfoLabel("It will analyze the data source previously added to the data source and index the forensic artifacts.")
        self.sp2 = SettingsUtils.createSeparators(1)

        self.p_method = SettingsUtils.createPanel()
        self.p_info.add(self.sp2, BorderLayout.SOUTH)
        self.p_info.add(self.lb_info, BorderLayout.SOUTH)
        self.p_info.add(self.lb_info2, BorderLayout.SOUTH)
        
        self.p_method.add(JLabel("Extract user data from:"))

        self.p_apps = SettingsUtils.createPanel(True)
        
        sorted_items = OrderedDict(sorted(Utils.get_all_packages().items()))

        for app, app_id in sorted_items.iteritems():
            #(app, app_id)
            checkbox = SettingsUtils.addApplicationCheckbox(app, app_id, self.getSelectedApps, visible = True)
            self.add(checkbox)
            self.apps_checkboxes_list.append(checkbox)
            self.p_apps.add(checkbox)
        
        self.add(self.p_method)
        self.add(self.p_apps)
        self.add(self.p_info)
        # end of checkboxes menu

    def customizeComponents(self):
        self.getSelectedApps("") #initialize selected apps
    
    def getSelectedApps(self, event):
        self.selected_apps = []
        
        for cb_app in self.apps_checkboxes_list:
            if cb_app.isSelected():
                self.selected_apps.append(cb_app.getActionCommand())

        #self.local_settings.setSetting("apps", json.dumps(selected_apps))
