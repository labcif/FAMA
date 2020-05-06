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



