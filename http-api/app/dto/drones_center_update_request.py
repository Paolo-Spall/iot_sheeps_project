import json

class TelemetryMessage:
    """
    Telemetry Message DTO class
    mapping the telemetry message data structure with:
    - timestamp: timestamp of the telemetry message
    - data_type: type of the telemetry message
    - value: value of the telemetry message
    """
    def __init__(self, timestamp, lat, lng, alt):
        self.timestamp = timestamp
        self.lat = lat
        self.lng= lng
        self.alt = alt

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)