import json


class NotificationMessageDescriptor:

    def __init__(self, timestamp, type, alerts):
        self.timestamp = timestamp
        self.type = type
        self.alerts = alerts

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
