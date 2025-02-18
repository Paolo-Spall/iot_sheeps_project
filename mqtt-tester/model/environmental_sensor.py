import random
import datetime
import json


class EnvironmentalSensor:
    def __init__(self, temperature_value=20.0, humidity_value=60.0, rain_probability=0):
        self.temperature_value = temperature_value
        self.humidity_value = humidity_value
        self.rain_probability = rain_probability

    def measure_environment(self):
        """Misura temperatura, umidità, probabilità di pioggia e registra l'orario."""
        self.temperature_value = round(max(min(self.temperature_value + random.uniform(-2, 2), 45), -10), 1)
        self.humidity_value = round(max(min(self.humidity_value + random.uniform(-2, 2), 100), 0), 1)
        self.rain_probability = max(min(self.rain_probability + int(random.uniform(-1.3, 1.3)), 5), 0)
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data e ora

    def get_json_data(self):
        """Restituisce i dati in un formato strutturato."""
        return json.dumps({
            "type": "ENVIRONMENTAL_SENSOR",
            "temperature_value": self.temperature_value,
            "temperature_udm": "°C",
            "humidity": self.humidity_value ,
            "rain_probability": self.rain_probability,
            "timestamp": self.timestamp
        })
    

