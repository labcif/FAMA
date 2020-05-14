import os
# from package.utils import Utils
# TODO -CHANGE, only for tests! avoid external libs from pip
try:
    import filetype
except:
    pass

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
        
    @staticmethod
    def get_category(filetype):

        if filetype in ["video/mp4","video/x-m4v","video/x-matroska","video/webm","video/quicktime","video/x-msvideo","video/x-ms-wmv","video/mpeg","video/x-flv"]: return "video"
        if filetype in ["image/jpeg","image/jpx","image/png","image/gif","image/webp","image/x-canon-cr2","image/tiff","image/bmp","image/vnd.ms-photo","image/vnd.adobe.photoshop","image/x-icon","image/heic"]: return "image"
        if filetype in ["audio/midi","audio/mpeg","audio/m4a","audio/ogg","audio/x-flac","audio/x-wav","audio/amr"]: return "audio"
        return "unknown"

    def add(self, path, from_web=False):
        media = {}
        media["path"] = path
        media["type"]="unknown"
        media["mime"]="unknown"

        if not from_web:
            media["path"]= os.path.join("Contents", path)
            try:
                file_type = filetype.guess(path) #TODO FIX PATH 
                if file_type:
                    media["type"]= self.get_category(file_type.mime)
                    media["mime"]= file_type.mime
            except:
                pass
        
        else:  #Web
            media["mime"]= "image/jpeg"
            media["type"]= self.get_category(media["mime"])

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

