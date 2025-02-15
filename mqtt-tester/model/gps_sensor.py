import random
import time
import json

class GPSSensor:

    def __init__(self):
        self.measure_position()
        self.type = "GPS_SENSOR"

    # Metodo per misurare la posizione
    def measure_position(self):
        # Simulazione di coordinate GPS casuali (X, Y, Z)
        self.x_position = random.uniform(-180.0, 180.0)  # Coordinate X tra -180 e 180
        self.y_position = random.uniform(-90.0, 90.0)    # Coordinate Y tra -90 e 90
        self.z_position = random.uniform(0.0, 10000.0)   # Coordinate Z (altitudine) tra 0 e 10.000 metri
        self.timestamp = int(time.time())  # Timestamp della misura
    
    def get_json_data(self):
        return json.dumps({"x": self.x_position, 
                "y": self.y_position, 
                "z": self.z_position, 
                "timestamp": self.timestamp,
                "type": self.type } )
