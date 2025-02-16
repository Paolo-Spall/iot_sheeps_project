import json
import requests
import paho.mqtt.client as mqtt
import yaml
import numpy as np
import os


# Default Configuration Dictionary
configuration_dict = {
    "broker_ip": "127.0.0.1",
    "broker_port": 1883,
    "gps_topic": "device/+/gps",
    "image_processing_topic": "device/+/image_processing",
    "publish_flock_center_topic": "service/flock_localization/flock_center",
    "publish_drones_center_topic": "service/flock_localization/drones_center",
    "device_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/location/l0001/device"
}


# Default Values
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONF_FILE_PATH = os.path.join(BASE_DIR, "system_monitoring_conf.yaml")

print(f"Trying to open: {CONF_FILE_PATH}")

if not os.path.exists(CONF_FILE_PATH):
    print("❌ File not found!")
    exit(1)

with open(CONF_FILE_PATH, 'r') as file:
    configuration_dict = yaml.safe_load(file)

print("Configuration loaded successfully.")

# Read Configuration from target Configuration File Path
def read_configuration_file():
    global configuration_dict

    with open(CONF_FILE_PATH, 'r') as file:
        configuration_dict = yaml.safe_load(file)

    return configuration_dict

configuration_dict = read_configuration_file()

print("Read Configuration from file ({}): {}".format(CONF_FILE_PATH, configuration_dict))

# MQTT Broker Configuration
mqtt_broker_host = configuration_dict["broker_ip"]
mqtt_broker_port = configuration_dict["broker_port"]
gps_topic = configuration_dict["gps_topic"]
image_processing_topic = configuration_dict["image_processing_topic"]
publish_flock_center_topic = configuration_dict["publish_flock_center_topic"]
publish_drones_center_topic = configuration_dict["publish_drones_center_topic"]


# HTTP API Configuration
api_url = configuration_dict["device_api_url"]


# Dati raccolti dai droni
gps_data = {}
image_processing_data = {}

# Funzione di conversione GPS → coordinate cartesiane
def gps_to_cartesian(lat, lon, lat_ref, lon_ref):
    R = 6371000  # Raggio della Terra in metri
    x = (lon - lon_ref) * (np.pi / 180) * R * np.cos(lat_ref * np.pi / 180)
    y = (lat - lat_ref) * (np.pi / 180