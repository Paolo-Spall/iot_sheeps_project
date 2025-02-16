import json


class MessageDescriptor:

    def __init__(self, timestamp, type, temperature_value, temperature_udm, humidity_value, rain_probability):
        self.timestamp = timestamp
        self.type = type
        self.temperature_value = temperature_value
        self.temperature_udm = temperature_udm
        self.humidity_value = humidity_value
        self.rain_probability = rain_probability

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)