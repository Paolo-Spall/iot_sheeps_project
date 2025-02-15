#!/usr/bin/bash

from .gps_sensor import GPSSensor
from .image_processing_system import ImageProcessingSensor
from .environmental_sensor import EnvironmentalSensor
import numpy as np
import json
import time

class Drone:
    max_velocity = np.ones(3)*10
    dt = 1.
    def __init__(self, id):
        self.id = id
        self.device_type = "drone"
        self.gps_sensor = GPSSensor()
        self.image_processing_sensor = ImageProcessingSensor()
        self.environmental_sensor = EnvironmentalSensor()

        self.position = np.array([0. ,0. , 0.])
    
    def update_position(self, control_input, dt=None):
        if dt is None:
            dt = self.dt
        control_velocity = np.array(control_input) * self.dt
        self.position = self.position + np.minimum(control_velocity , self.max_velocity)

    def read_sensors(self):
        self.gps_sensor.measure_position()
        self.image_processing_sensor.measure_distance()
        self.environmental_sensor.measure_environment()
    
    def get_environmental_data(self):
        return self.environmental_sensor.get_json_data()
    
    def get_gps_data(self):
        return self.gps_sensor.get_json_data()
    
    def get_image_processing_data(self):
        return self.image_processing_sensor.get_json_data()
    
    def get_drone_data(self):
        return json.dumps({
            "id": self.id,
            "device_type": self.device_type,
        })
    
    def get_drone_position(self):
        return json.dumps({
            "type": "DRONE_POSITION",
            "x" : self.position[0],
            "y" : self.position[1],
            "z" : self.position[2],
            "timestamp": int(time.time())
        })

