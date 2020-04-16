def get_value(entry):
    try:
        return int(entry['timestamp'])
    except KeyError:
            return 0

class Timeline:
    def __init__(self):
        self.timeline = []
    

    def add(self, timestamp, obj):
        entry= {
            "timestamp": timestamp,
            "value": obj 
            }
        self.timeline.append(entry)


    def get_sorted_timeline(self, reverse=False):
        self.timeline.sort(key=get_value, reverse=reverse)
        return self.timeline



