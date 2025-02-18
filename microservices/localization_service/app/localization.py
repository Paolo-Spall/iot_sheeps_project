import json
import paho.mqtt.client as mqtt
import yaml
import numpy as np
import os
from math import radians, degrees, sin, cos

# Default Configuration Dictionary
configuration_dict = {
    "broker_ip": "127.0.0.1",
    "broker_port": 1883,
    "cartesian_topic": "drone/+/telemetry/cartesian",
    "image_processing_topic": "drone/+/telemetry/image_processing",
    "publish_flock_center_topic": "service/flock_localization/flock_center",
    "publish_drones_center_gps_topic": "service/flock_localization/drones_center_gps",
    "publish_drones_center_cartesian_topic": "service/flock_localization/drones_center_cartesian",
    "device_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/location/l0001/device"
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONF_FILE_PATH = os.path.join(BASE_DIR, "localization_conf.yaml")

if not os.path.exists(CONF_FILE_PATH):
    print("❌ File not found!")
    exit(1)

with open(CONF_FILE_PATH, 'r') as file:
    configuration_dict = yaml.safe_load(file)

# Read Configuration from file
def read_configuration_file():
    with open(CONF_FILE_PATH, 'r') as file:
        return yaml.safe_load(file)

# Convert Cartesian to GPS
def cartesian_to_gps(lat_ref, lng_ref, x, y, z):
    R = 6378137
    lat_ref_rad, lon_ref_rad = radians(lat_ref), radians(lng_ref)
    new_lat = degrees(lat_ref_rad + (y / R))
    new_lng = degrees(lon_ref_rad + (x / (R * cos(lat_ref_rad))))
    return new_lat, new_lng, z

configuration_dict = read_configuration_file()

# MQTT Configuration
mqtt_broker_host = configuration_dict["broker_ip"]
mqtt_broker_port = configuration_dict["broker_port"]
cartesian_topic = configuration_dict["cartesian_topic"]
image_processing_topic = configuration_dict["image_processing_topic"]
publish_flock_center_topic = configuration_dict["publish_flock_center_topic"]
publish_drones_center_gps_topic = configuration_dict["publish_drones_center_gps_topic"]
publish_drones_center_cartesian_topic = configuration_dict["publish_drones_center_cartesian_topic"]

# Data storage
cartesian_drones_data, image_processing_data = {}, {}

# Compute flock position
def calculate_flock_position(timestamp):
    if len(cartesian_drones_data) < 3 or len(image_processing_data) < 3:
        print("⚠️ Non ho abbastanza dati per calcolare la posizione del gregge")
        return

    points = np.array([[data["x"], data["y"], data["z"]] for data in cartesian_drones_data.values()])
    sorted_keys = sorted(image_processing_data.keys())
    distances = np.array([image_processing_data[key]["distance"] for key in sorted_keys])
    weights = 1 / distances
    flock_x, flock_y, flock_z = (np.sum(points[:, i] * weights) / np.sum(weights) for i in range(3))
    flock_position = {"x": float(flock_x), "y": float(flock_y), "z": float(flock_z)}

    payload = json.dumps({"timestamp": timestamp, "type": "FLOCK_POSITION", **flock_position})
    client.publish(publish_flock_center_topic, payload)
    print(f"📤 Published to '{publish_flock_center_topic}': {payload}")
    cartesian_drones_data.clear()
    image_processing_data.clear()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(cartesian_topic)
    client.subscribe(image_processing_topic)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        drone_id = msg.topic.split('/')[1]
        timestamp = payload.get("timestamp", None)

        if mqtt.topic_matches_sub(cartesian_topic, msg.topic):
            cartesian_drones_data[drone_id] = payload
        elif mqtt.topic_matches_sub(image_processing_topic, msg.topic):
            image_processing_data[drone_id] = payload

        if len(cartesian_drones_data) == 3 and len(image_processing_data) == 3:
            avg_x, avg_y, avg_z = (np.mean([cartesian_drones_data[key][i] for key in cartesian_drones_data]) for i in ("x", "y", "z"))
            drones_center = {"x": float(avg_x), "y": float(avg_y), "z": float(avg_z)}

            payload_cartesian = json.dumps({"timestamp": timestamp, "type": "DRONES_CENTER_CARTESIAN", **drones_center})
            client.publish(publish_drones_center_cartesian_topic, payload_cartesian)
            print(f"📤 Published to '{publish_drones_center_cartesian_topic}': {payload_cartesian}")

            lat_ref, lng_ref = 31.5395378, -110.7561963
            avg_lat, avg_lng, avg_alt = cartesian_to_gps(lat_ref, lng_ref, avg_x, avg_y, avg_z)
            drones_center_gps = {"lat": float(avg_lat), "lng": float(avg_lng), "alt": float(avg_alt)}

            payload_gps = json.dumps({"timestamp": timestamp, "type": "DRONES_CENTER_GPS", **drones_center_gps})
            client.publish(publish_drones_center_gps_topic, payload_gps)
            print(f"📤 Published to '{publish_drones_center_gps_topic}': {payload_gps}")

            calculate_flock_position(timestamp)
    except json.JSONDecodeError:
        print("❌ Errore nel decodificare il payload JSON")
    except KeyError as e:
        print(f"❌ Chiave mancante nel payload: {e}")
    except Exception as e:
        print(f"❌ Error processing MQTT message: {str(e)}")

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(mqtt_broker_host, mqtt_broker_port, 60)
client.loop_forever()
