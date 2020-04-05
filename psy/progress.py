from org.sleuthkit.autopsy.casemodule.services.FileManager import FileAddProgressUpdater

class ProgressUpdater(FileAddProgressUpdater):
    def __init__(self):
        self.files = []
        pass
    
    def fileAdded(self, newfile):
        self.files.append(newfile)
        
    def getFiles(self):
        return self.files