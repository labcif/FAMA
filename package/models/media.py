import os

class Media:
    def __init__(self):
        self.media = []

    def add(self, path, from_web=False):
        if not from_web:
            path = os.path.join("Contents", path)
        
        self.media.append(path)
    
    def get_media(self):
        return self.media

