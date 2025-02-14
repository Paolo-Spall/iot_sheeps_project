import random
import datetime


class EnvironmentalSensor:
    def __init__(self):
        self.measure_environment()

    def measure_environment(self):
        """Misura temperatura, umidità, probabilità di pioggia e registra l'orario."""
        self.temperature_value = round(random.uniform(20.0, 40.0), 1)  # °C
        self.humidity_value = round(random.uniform(30.0, 90.0), 1)  # % di umidità
        self.rain_probability = random.randint(1, 5)  # Scala da 1 a 5
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data e ora

    def get_data(self):
        """Restituisce i dati in un formato strutturato."""
        return {
            "temperature": f"{self.temperature_value} °C",
            "humidity": f"{self.humidity_value} %",
            "rain_probability": self.rain_probability,
            "timestamp": self.timestamp
        }
    

