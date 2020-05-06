import os

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

    def get_sorted_locations(self, reverse=False):
        self.locations.sort(key=self.get_value, reverse=reverse)
        return self.locations


class Media:
    def __init__(self):
        self.media = []

    def add(self, path, from_web=False):
        if not from_web:
            path = os.path.join("Contents", path)
        
        self.media.append(path)
    
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

    def get_sorted_timeline(self, reverse=False):
        self.timeline.sort(key=self.get_value, reverse=reverse)
        return self.timeline

