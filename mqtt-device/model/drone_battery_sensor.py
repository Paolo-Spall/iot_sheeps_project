import random as r

class Drone_battery_sensor:
    dt = 0.1

    def __init__(self):
        self.battery = 100

    # Another instance method with a parameter
    def measure_battery(self):
        self.battery = max(0,self.battery + r.uniform(-1, 0))