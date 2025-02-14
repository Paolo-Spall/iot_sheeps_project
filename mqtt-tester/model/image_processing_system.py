import random
import time

class ImageProcessingSensor:

    def __init__(self):
        self.measure_distance()

    # Metodo per misurare la distanza dal centro del gregge
    def measure_distance(self):
        # Simulazione di una distanza casuale tra 10 e 100 metri
        self.distance_to_flock_center = random.uniform(10.0, 100.0)  # Distanza in metri
        self.unit_of_measurement = "meters"  # Unità di misura
        self.timestamp = int(time.time())  # Timestamp della misura
