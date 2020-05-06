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



