import logging

from java.util import UUID
from java.awt import Component
from javax.swing import JPanel
from javax.swing import JCheckBox
from javax.swing import JRadioButton
from javax.swing import JTextArea
from javax.swing import BoxLayout
from javax.swing.border import EmptyBorder

from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.datamodel import CommunicationsManager
from org.sleuthkit.autopsy.geolocation.datamodel import BookmarkWaypoint
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.autopsy.coreutils import Version

from psy.progress import ProgressUpdater

class PsyUtils:
    @staticmethod
    def post_message(msg):
        IngestServices.getInstance().postMessage(IngestMessage.createMessage(IngestMessage.MessageType.DATA, "Forensics Analyzer", msg))

    @staticmethod
    def add_to_fileset(name, folder, device_id = UUID.randomUUID(), progress_updater = ProgressUpdater(), notify = True):
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        skcase_data = Case.getCurrentCase()
        #skcase_data.notifyAddingDataSource(device_id)
        #progress_updater = ProgressUpdater() 
        
        data_source = fileManager.addLocalFilesDataSource(device_id.toString(), name, "", folder, progress_updater)
        
        if notify:
            files_added = progress_updater.getFiles()
            for file_added in files_added:
                skcase_data.notifyDataSourceAdded(file_added, device_id)

        return data_source

    @staticmethod
    def create_attribute_type(att_name, type, att_desc):
        try:
            Case.getCurrentCase().getSleuthkitCase().addArtifactAttributeType(att_name, type, att_desc)
        except:
            logging.warning("Error creating attribute type: " + att_desc)
        return Case.getCurrentCase().getSleuthkitCase().getAttributeType(att_name)
 
    @staticmethod
    def create_artifact_type(base_name, art_name, art_desc):
        try:
            Case.getCurrentCase().getSleuthkitCase().addBlackboardArtifactType(art_name, base_name.capitalize() + art_desc)
        except:
            logging.warning("Error creating artifact type: " + art_desc)
        art = Case.getCurrentCase().getSleuthkitCase().getArtifactType(art_name)
        return art

    @staticmethod
    def get_artifacts_list():
        listing = []
        try:
            listing = Case.getCurrentCase().getSleuthkitCase().getArtifactTypesInUse()
        except:
            logging.warning("Error getting artifacts list")

        return listing
    
    @staticmethod
    def index_artifact(artifact, artifact_type):
        try:
            Case.getCurrentCase().getServices().getBlackboard().indexArtifact(artifact)
        except:
            logging.warning("Error indexing artifact type: " + artifact_type)
        IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent("Forensics Analyzer",artifact_type, None))

    @staticmethod
    def add_relationship(node1, node2, art, relationship_type, timestamp):
        Case.getCurrentCase().getSleuthkitCase().getCommunicationsManager().addRelationships(node1, node2, art, relationship_type, timestamp)
    
    @staticmethod
    def add_tracking_point(file, timestamp=0, latitude=0, longitude=0, altitude=0, source="source"):
        
        art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_GPS_TRACKPOINT)
        art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_GEO_LATITUDE, source, float(latitude)))
        art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_GEO_LONGITUDE, source, float(longitude)))
        art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_GEO_ALTITUDE, source, float(altitude)))
        art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, source, timestamp))
        BookmarkWaypoint(art)
        return art


                    
    @staticmethod
    def blackboard_attribute(attribute):
        return {
            "byte": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.BYTE,
            "datetime": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME,
            "double": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DOUBLE,
            "integer": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.INTEGER,
            "long": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG,
            "string": BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING
        }.get(attribute)
    
    @staticmethod
    def get_or_create_account(account_type, file, uniqueid):
        return Case.getCurrentCase().getSleuthkitCase().getCommunicationsManager().createAccountFileInstance(account_type, uniqueid, "test", file.getDataSource())

    @staticmethod
    def add_account_type(accountTypeName, displayName):
        communication_manager = Case.getCurrentCase().getSleuthkitCase().getCommunicationsManager()
        return CommunicationsManager.addAccountType(communication_manager,accountTypeName, displayName)

    @staticmethod
    def get_autopsy_version():
        item = {"major": 0, "minor": 0, "patch": 0}

        version = Version.getVersion().split('.')
        
        try:
            if len(version) >= 1:
                item["major"] = int(version[0])
            
            if len(version) >= 2:
                item["minor"] = int(version[1])

            if len(version) >= 3:
                item["patch"] = int(version[2])
        except:
            pass
        
        return item


class SettingsUtils:
    @staticmethod
    def createPanel(scroll = False, ptop = 0, pleft = 0, pbottom = 0, pright = 0):
        panel = JPanel()
        panel.setLayout(BoxLayout(panel, BoxLayout.PAGE_AXIS))
        panel.setAlignmentX(Component.LEFT_ALIGNMENT)
        panel.setBorder(EmptyBorder(ptop, pleft, pbottom, pright))
        
        # if scroll:
            # scrollpane = JScrollPane(panel)
            # scrollpane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            # scrollpane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_NEVER)
            # return JPanel().add(scrollpane)
        
        return panel

    @staticmethod
    def addApplicationCheckbox(app, app_id, ap, visible = False):
        checkbox = JCheckBox("{} ({})".format(app.capitalize(), app_id), actionPerformed= ap)
        checkbox.setActionCommand(app)
        checkbox.setSelected(True)
        checkbox.setVisible(visible)
        checkbox.setActionCommand(app_id)
        return checkbox

    @staticmethod
    def addDeviceCheckbox(device, ap, visible = False):
        checkbox = JCheckBox(device, actionPerformed= ap)
        checkbox.setActionCommand(device)
        checkbox.setSelected(True)
        checkbox.setVisible(visible)
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
        textArea.setText(text)
        return textArea

    @staticmethod
    def createSeparators(count):
        lines =""
        for i in range(count):
            lines+="<br>"

        return SettingsUtils.createInfoLabel(lines)