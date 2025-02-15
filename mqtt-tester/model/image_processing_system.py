import random
import time
import json

class ImageProcessingSensor:

    def __init__(self):
        self.measure_distance()
        self.type = "IMAGE_PROCESSING_SENSOR"

    # Metodo per misurare la distanza dal centro del gregge
    def measure_distance(self):
        # Simulazione di una distanza casuale tra 10 e 100 metri
        self.distance_to_flock_center = random.uniform(10.0, 100.0)  # Distanza in metri
        self.unit_of_measurement = "meters"  # Unità di misura
        self.timestamp = int(time.time())  # Timestamp della misura
    
    def get_json_data(self):
        return json.dumps(
            {"distance": self.distance_to_flock_center,
             "unit": self.unit_of_measurement,
             "timestamp": self.timestamp,
             "type": self.type } )
