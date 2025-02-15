import random
import time
import json


class EnvironmentalSensor:
    def __init__(self):
        self.measure_environment()
        self.type = "ENVIRONMENTAL_SENSOR"

    def measure_environment(self):
        """Misura temperatura, umidità, probabilità di pioggia e registra l'orario."""
        self.temperature_value = round(random.uniform(20.0, 40.0), 1)  # °C
        self.humidity_value = round(random.uniform(30.0, 90.0), 1)  # % di umidità
        self.rain_probability = random.randint(1, 5)  # Scala da 1 a 5
        self.timestamp = int(time.time())

    def get_json_data(self):
        """Restituisce i dati in un formato strutturato."""
        return json.dumps({
            "temperature": f"{self.temperature_value}",
            "humidity": f"{self.humidity_value}",
            "rain_probability": self.rain_probability,
            "timestamp": self.timestamp,
            "type": self.type
        })
    

