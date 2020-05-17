import os
from package.utils import Utils

class Location:
    def __init__(self):
        self.locations = []
    
    def add(self, timestamp=0, latitude=0, longitude=0, altitude=0):
        entry = {
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude" : altitude
        }
        self.locations.append(entry)

    def get_value(self, entry):
        try:
            return int(entry['timestamp'])
        except KeyError:
            return 0

    def get_sorted_locations(self, reverse=True):
        self.locations.sort(key=self.get_value, reverse=reverse)
        return self.locations


class Media:
    def __init__(self):
        self.media = []

    def add(self, path):
        media = {}
        media["path"] = path
        media["type"] = "unknown"

        if os.path.exists(path) or Utils.is_url(path):
            #media["path"] = os.path.join("Contents", path)
            media["type"] = Utils.get_media_type(path)
         
        self.media.append(media)
    
    def get_media(self):
        return self.media

class Timeline:
    def __init__(self):
        self.timeline = []

    def add(self, timestamp, event, obj):
        entry = {
            "timestamp": timestamp,
            "event": str(event),
            "value": obj 
        }   	
        self.timeline.append(entry)

    def get_value(self, entry):
        try:
            return int(entry['timestamp'])
        except KeyError:
            return 0

    def get_sorted_timeline(self, reverse=True):
        self.timeline.sort(key=self.get_value, reverse=reverse)
        return self.timeline

