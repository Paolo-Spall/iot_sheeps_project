#!/usr/bin/bash

from .image_processing_system import ImageProcessingSensor
from .environmental_sensor import EnvironmentalSensor
import numpy as np
import json
import time


class Drone:
    max_velocity = np.ones(3) * 10
    dt = 0.1
    # Coordinate GPS della fattoria
    lat0 = 45.123456  # Sostituisci con la latitudine della fattoria
    lng0 = 9.654321

    def __init__(self, id):
        self.id = id
        self.device_type = "drone"
        self.image_processing_sensor = ImageProcessingSensor()
        self.environmental_sensor = EnvironmentalSensor()

        self.position = np.array([0., 0., 0.])

    def update_position(self, control_input, dt=None):
        if dt is None:
            dt = self.dt
        print(control_input)
        control_velocity = np.array(control_input) * self.dt
        self.position = self.position + np.clip(control_velocity, -self.max_velocity, self.max_velocity)

    def get_gps_data(self):
        """ Converte x, y in latitudine e longitudine, mantenendo z come altitudine """
        lat = self.lat0 + (self.position[1] / 111320)  # 111320m ≈ 1° di latitudine
        lng = self.lng0 + (self.position[0] / (111320 * np.cos(np.radians(self.lat0))))  # Corregge per la latitudine
        alt = self.position[2]

        return json.dumps({
            "id": self.id,
            "lat": lat,
            "lng": lng,
            "alt": alt
        })

    def read_sensors(self):
        self.image_processing_sensor.measure_distance()
        self.environmental_sensor.measure_environment()

    def get_environmental_data(self):
        return self.environmental_sensor.get_json_data()


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
            "x": self.position[0],
            "y": self.position[1],
            "z": self.position[2],
            "timestamp": int(time.time())
        })
# Da togliere quando inseriamo microservizio
#    def get_drone_center_position(self):
#        return json.dumps({
#            "type": "DRONES_CENTER",
#            "x" : self.position[0],
#            "y" : self.position[1],
#            "z" : self.position[2],
#            "timestamp": int(time.time())
#        })

