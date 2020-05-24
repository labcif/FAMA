import threading
import logging
import time
from collections import OrderedDict

from java.awt import Font
from java.awt import Dimension
from java.awt import BorderLayout
from javax.swing import JPanel
from javax.swing import JSeparator
from javax.swing import JButton
from javax.swing import BoxLayout
from javax.swing import JLabel
from javax.swing.border import EmptyBorder
from java.beans import PropertyChangeSupport
from org.sleuthkit.autopsy.corecomponentinterfaces import DataSourceProcessorCallback
from org.sleuthkit.autopsy.corecomponentinterfaces import DataSourceProcessor  

from package.utils import Utils
from package.device import DeviceCommunication
from psy.psyutils import SettingsUtils, PsyUtils
from psy.extractor import Extractor

class DataSourcesPanelSettings(JPanel):
    serialVersionUID = 1L

    def __init__(self):
        self.pcs = PropertyChangeSupport(self)

        self.initComponents()
        self.customizeComponents()

    def getVersionNumber(self):
        return serialVersionUID

    #PROCESSOR LOGIC
    def run(self, progressMonitor, callback):
        threading.Thread(target=self.running, args=[progressMonitor, callback]).start()

    def running(self, progressMonitor, callback):
        progressMonitor.setIndeterminate(True)
        newDataSources = []
        errors = []
        result = DataSourceProcessorCallback.DataSourceProcessorResult.NO_ERRORS

        try:
            extractor = Extractor(self.selected_apps, self.selected_devices, progressMonitor)
            folders = extractor.dump_apps()

            for serial, folder in folders.items():
                try:
                    data_source = PsyUtils.add_to_fileset("ADB_{}_{}".format(serial, int(time.time())), folder, notify = False)
                    newDataSources.append(data_source)
                except Exception as e:
                    message = "Extractor Failed for {} for {}!".format(serial, e)
                    logging.error(message)
                    errors.append(message)
                    result = DataSourceProcessorCallback.DataSourceProcessorResult.NONCRITICAL_ERRORS
        
        except Exception as e:
            message = "Global Extractor Failed. Aborting: {}".format(e)
            logging.error(message)
            errors.append(message)
            result = DataSourceProcessorCallback.DataSourceProcessorResult.CRITICAL_ERRORS
        
        if len(newDataSources) == 0:
            result = DataSourceProcessorCallback.DataSourceProcessorResult.CRITICAL_ERRORS

        callback.done(result, errors, newDataSources)

    #PROCESSOR JPANEL LOGIC
    def addPropertyChangeListener(self, pcl):
        super(DataSourcesPanelSettings, self).addPropertyChangeListener(pcl)
        self.pcs.addPropertyChangeListener(pcl)

    def fireUIUpdate(self):
        #Fire UI change, this is necessary to know if it's allowed to click next
        self.pcs.firePropertyChange(DataSourceProcessor.DSP_PANEL_EVENT.UPDATE_UI.toString(), False, True);        

    def validatePanel(self):
        return (len(self.selected_apps) != 0 and len(self.selected_devices) != 0)

    def initComponents(self):
        self.apps_checkboxes_list = []
        self.devices_checkboxes_list = []
        self.selected_apps = []
        self.selected_devices = []

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))
        self.setPreferredSize(Dimension(543, 172)) #Max 544x173 https://www.sleuthkit.org/autopsy/docs/api-docs/3.1/interfaceorg_1_1sleuthkit_1_1autopsy_1_1corecomponentinterfaces_1_1_data_source_processor.html#a068919818c017ee953180cc79cc68c80
        
        # info menu
        self.p_info = SettingsUtils.createPanel()
        self.p_info.setPreferredSize(Dimension(543,172))
        self.d_method = SettingsUtils.createPanel(pbottom = 15)

        self.label = JLabel('Press "Find Devices" to search for devices to extract information.')
        self.label.setBorder(EmptyBorder(0,0,5,0))
        self.d_method.add(self.label)

        self.label = JLabel('It will generate a file set per device.')
        self.label.setBorder(EmptyBorder(0,0,10,0))
        self.d_method.add(self.label)

        self.label = JLabel('This extract method requires ADB enabled on the device and may require root privilege for some paths.')
        self.label.setFont(self.label.getFont().deriveFont(Font.BOLD, 11))
        self.label.setBorder(EmptyBorder(0,0,10,0))
        self.d_method.add(self.label)

        self.search_devices = JButton('Find Devices', actionPerformed = self.findDevices)
        self.d_method.add(self.search_devices)

        self.p_method = SettingsUtils.createPanel(ptop = 15)

        self.sp2 = SettingsUtils.createSeparators(0)
        self.p_info.add(self.sp2, BorderLayout.SOUTH)

        self.p_method.add(JLabel("Extract user data from:"))

        self.p_apps = SettingsUtils.createPanel(True, pbottom = 10)
        self.p_devices = SettingsUtils.createPanel(True)
        self.choose_device = JLabel("Choose device:")
        self.choose_device.setVisible(False)

        self.appsBlock()
        
        self.add(self.d_method)
        self.add(JSeparator())
        self.add(self.p_method)
        self.add(self.p_apps)
        
        self.add(self.choose_device)
        self.add(self.p_devices)

        self.add(self.p_info)

        self.findDevices("")

    def customizeComponents(self):
        self.updateCheckboxes("")
    
    def updateCheckboxes(self, event):
        self.getSelectedApps(event) #initialize selected apps
        self.getSelectedDevices(event) #initialize selected devices
        self.fireUIUpdate()

    def findDevices(self, event):
        self.p_devices.removeAll()
        self.devices_checkboxes_list = []

        devices = DeviceCommunication.list_devices()
        for device in devices:
            checkbox = SettingsUtils.addDeviceCheckbox(device, self.updateCheckboxes, visible = True)
            self.devices_checkboxes_list.append(checkbox)
            self.p_devices.add(checkbox)

        self.choose_device.setVisible(len(self.devices_checkboxes_list) > 0)

        #refresh list
        self.p_devices.setVisible(False)
        self.p_devices.setVisible(True)

        self.updateCheckboxes(event)

    def appsBlock(self):
        sorted_items = OrderedDict(sorted(Utils.get_all_packages().items()))
        for app, app_id in sorted_items.iteritems():
            #(app, app_id)
            checkbox = SettingsUtils.addApplicationCheckbox(app, app_id, self.updateCheckboxes, visible = True)
            #self.add(checkbox)
            self.apps_checkboxes_list.append(checkbox)
            self.p_apps.add(checkbox)

    def getSelectedDevices(self, event):
        self.selected_apps = []
        
        for cb_app in self.apps_checkboxes_list:
            if cb_app.isSelected():
                self.selected_apps.append(cb_app.getActionCommand())

    def getSelectedApps(self, event):
        self.selected_devices = []
        
        for cb_app in self.devices_checkboxes_list:
            if cb_app.isSelected():
                self.selected_devices.append(cb_app.getActionCommand())


    