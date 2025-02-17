import json
import requests
import paho.mqtt.client as mqtt
import yaml
import numpy as np
import os
from math import radians, degrees, sin, cos, atan2, sqrt

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

# Default Values
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONF_FILE_PATH = os.path.join(BASE_DIR, "localization_conf.yaml")
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

def cartesian_to_gps(self, lat_ref, lng_ref, x, y, z):
        """ Converte x, y in latitudine e longitudine, mantenendo z come altitudine """
        R = 6378137

        lat_ref_rad = radians(lat_ref)
        lon_ref_rad = radians(lng_ref)

        # Calcola il nuovo punto in coordinate geografiche
        new_lat_rad = lat_ref_rad + (y / R)
        new_lon_rad = lon_ref_rad + (x / (R * cos(lat_ref_rad)))

        # Converti il risultato in gradi
        new_lat = degrees(new_lat_rad)
        new_lng = degrees(new_lon_rad)

        return new_lat, new_lng , z

configuration_dict = read_configuration_file()
print("Read Configuration from file ({}): {}".format(CONF_FILE_PATH, configuration_dict))

# MQTT Broker Configuration
mqtt_broker_host = configuration_dict["broker_ip"]
mqtt_broker_port = configuration_dict["broker_port"]
cartesian_topic = configuration_dict["cartesian_topic"]
image_processing_topic = configuration_dict["image_processing_topic"]
publish_flock_center_topic = configuration_dict["publish_flock_center_topic"]
publish_drones_center_gps_topic = configuration_dict["publish_drones_center_gps_topic"]
publish_drones_center_cartesian_topic = configuration_dict["publish_drones_center_cartesian_topic"]

# HTTP API Configuration
api_url = configuration_dict["device_api_url"]

# Dati raccolti dai droni
cartesian_drones_data = {}
image_processing_data = {}

# Calcolo della posizione del gregge (in coordinate cartesiane: x, y, z)
def calculate_flock_position(timestamp):
    global cartesian_drones_data, image_processing_data
    if len(cartesian_drones_data) < 3 or len(image_processing_data) < 3:
        print("⚠️ Non ho abbastanza dati per calcolare la posizione del gregge")
        return

    # Estraggo le distanze dal centro del gregge dai dati di image processing
    distances = np.array([
        image_processing_data[key]["distance"]
        for key in sorted(image_processing_data.keys())
    ])

    # Trilaterazione (media pesata)
    weights = 1 / distances
    flock_x = np.sum(cartesian_drones_data[:, 0] * weights) / np.sum(weights)
    flock_y = np.sum(cartesian_drones_data[:, 1] * weights) / np.sum(weights)
    flock_z = np.sum(cartesian_drones_data[:, 2] * weights) / np.sum(weights)

    flock_position = {"x": float(flock_x), "y": float(flock_y), "z": float(flock_z)}
    print(f"📌 Calculated flock position: {flock_position}")

    # Pubblica la posizione del gregge in coordinate cartesiane (x, y, z)
    payload_string_flock = json.dumps({
        "timestamp": timestamp,
        "type": "FLOCK_POSITION",
        "x": flock_position["x"],
        "y": flock_position["y"],
        "z": flock_position["z"]
    })

    client.publish(publish_flock_center_topic, payload_string_flock)
    print(f"📤 Published to '{publish_flock_center_topic}': {payload_string_flock}")

    # Svuoto i dati per il prossimo ciclo
    cartesian_drones_data.clear()
    image_processing_data.clear()

# Callback per la connessione al broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(cartesian_topic)
    client.subscribe(image_processing_topic)

# Callback per la ricezione dei messaggi MQTT
def on_message(client, userdata, msg):
    global cartesian_drones_data, image_processing_data
    try:
        payload = json.loads(msg.payload.decode())
        drone_id = msg.topic.split('/')[1]
        timestamp = payload.get("timestamp", None)
        print(f"📥 Received message from {drone_id} on {msg.topic}: {payload}")

        # Salvo i dati in base al topic
        if mqtt.topic_matches_sub(cartesian_topic, msg.topic):
            cartesian_drones_data[drone_id] = payload
        elif mqtt.topic_matches_sub(image_processing_topic, msg.topic):
            image_processing_data[drone_id] = payload

        print(f"📥 Updated data: Cartesian({len(cartesian_drones_data)}) - Image Processing({len(image_processing_data)})")
        print("GPS Data:", cartesian_drones_data)
        print("Image Processing Data:", image_processing_data)

        # Calcolo del centro dei droni se ho almeno 3 dati GPS e 3 dati di image processing
        if len(cartesian_drones_data) == 3 and len(image_processing_data) == 3:
            # Calcolo della media in per DRONES_CENTER (con chiavi lat, lng, alt)
            avg_x = np.mean([cartesian_drones_data[key]["x"] for key in cartesian_drones_data])
            avg_y = np.mean([cartesian_drones_data[key]["y"] for key in cartesian_drones_data])
            avg_z = np.mean([cartesian_drones_data[key]["z"] for key in cartesian_drones_data])

            drones_center = {
                "x": float(avg_x),
                "y": float(avg_y),
                "z": float(avg_z),
            }
            print(f"📌 Calculated drones center position cartesian: {drones_center}")

            payload_string_drones = json.dumps({
                "timestamp": timestamp,
                "type": "DRONES_CENTER_CARTESIAN",
                "x": drones_center["x"],
                "y": drones_center["y"],
                "z": drones_center["z"]
            })
            client.publish(publish_drones_center_cartesian_topic, payload_string_drones)
            print(f"📤 Published to '{publish_drones_center_cartesian_topic}': {payload_string_drones}")

            # Calcolo della media in coordinate gps (lat, lon) utilizzando la fattoria come riferimento
            lat_ref = 31.5395378
            lng_ref = -110.7561963

            avg_lat, avg_lng, avg_alt = cartesian_to_gps(lat_ref, lng_ref, avg_x, avg_y, avg_z)
            drones_center_gps = {
                "lat": float(avg_lat),
                "lng": float(avg_lng),
                "alt": float(avg_alt),
            }

            print(f"📌 Calculated drones center position (gps): {drones_center_gps}")

            payload_string_gps = json.dumps({
                "timestamp": timestamp,
                "type": "DRONES_CENTER_CARTESIAN",
                "lat": drones_center_gps["lat"],
                "lng": drones_center_gps["lng"],
                "alt": drones_center_gps["alt"]
            })

            client.publish(publish_drones_center_gps_topic, payload_string_gps)
            print(f"📤 Published to '{publish_drones_center_gps_topic}': {payload_string_gps}")

            # Se ho tutti i dati, calcolo anche la posizione del gregge
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

print("Subscribing to topics:")
print("Image Processing Topic:", image_processing_topic)
print("Cartesian Topic:", cartesian_topic)

# Connect to MQTT Broker
client.connect(mqtt_broker_host, mqtt_broker_port, 60)

# Start the MQTT loop
client.loop_forever()
