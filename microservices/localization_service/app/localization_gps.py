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
    "gps_topic": "drone/+/telemetry/cartesian",
    "image_processing_topic": "drone/+/telemetry/image_processing",
    "publish_flock_center_topic": "service/flock_localization/flock_center",
    "publish_drones_center_topic": "service/flock_localization/drones_center",
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

configuration_dict = read_configuration_file()
print("Read Configuration from file ({}): {}".format(CONF_FILE_PATH, configuration_dict))

# MQTT Broker Configuration
mqtt_broker_host = configuration_dict["broker_ip"]
mqtt_broker_port = configuration_dict["broker_port"]
gps_topic = configuration_dict["gps_topic"]
image_processing_topic = configuration_dict["image_processing_topic"]
publish_flock_center_topic = configuration_dict["publish_flock_center_topic"]
publish_drones_center_topic = configuration_dict["publish_drones_center_topic"]
publish_drones_center_cartesian_topic = configuration_dict["publish_drones_center_cartesian_topic"]

# HTTP API Configuration
api_url = configuration_dict["device_api_url"]

# Dati raccolti dai droni
gps_data = {}
image_processing_data = {}

# Funzione di conversione GPS → coordinate cartesiane
def gps_to_cartesian(lat, lon, lat_ref, lon_ref):
    R = 6371000  # Raggio della Terra in metri
    x = (lon - lon_ref) * (np.pi / 180) * R * np.cos(lat_ref * np.pi / 180)
    y = (lat - lat_ref) * (np.pi / 180) * R
    return x, y

# Calcolo della posizione del gregge (in coordinate cartesiane: x, y, z)
def calculate_flock_position(timestamp):
    global gps_data, image_processing_data
    if len(gps_data) < 3 or len(image_processing_data) < 3:
        print("⚠️ Non ho abbastanza dati per calcolare la posizione del gregge")
        return

    # Uso il punto fisso (0,0) come riferimento
    lat_ref, lon_ref = 0, 0

    # Converto GPS → (x, y) usando (0,0) come riferimento
    gps_positions = np.array([
        gps_to_cartesian(gps_data[key]["lat"], gps_data[key]["lng"], lat_ref, lon_ref)
        for key in gps_data
    ])

    # Estraggo le distanze dal centro del gregge dai dati di image processing
    distances = np.array([
        image_processing_data[key]["distance"]
        for key in sorted(image_processing_data.keys())
    ])

    # Trilaterazione (media pesata)
    weights = 1 / distances
    flock_x = np.sum(gps_positions[:, 0] * weights) / np.sum(weights)
    flock_y = np.sum(gps_positions[:, 1] * weights) / np.sum(weights)

    # Calcolo dell'altezza media (z) dai dati GPS
    flock_z = np.mean([gps_data[key].get("alt", 0) for key in gps_data])
    flock_position = {"x": float(flock_x), "y": float(flock_y), "z": float(flock_z)}
    print(f"📌 Calculated flock position: {flock_position}")

    # Pubblica la posizione del gregge in coordinate cartesiane (x, y, z)
    payload_string_flock = json.dumps({
        "timestamp": timestamp,
        "type": "FLOCK_POSITION",
        "value": flock_position
    })

    client.publish(publish_flock_center_topic, payload_string_flock)
    print(f"📤 Published to '{publish_flock_center_topic}': {payload_string_flock}")

    # Svuoto i dati per il prossimo ciclo
    gps_data.clear()
    image_processing_data.clear()

# Callback per la connessione al broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(gps_topic)
    client.subscribe(image_processing_topic)

# Callback per la ricezione dei messaggi MQTT
def on_message(client, userdata, msg):
    global gps_data, image_processing_data
    try:
        payload = json.loads(msg.payload.decode())
        drone_id = msg.topic.split('/')[1]
        timestamp = payload.get("timestamp", None)
        print(f"📥 Received message from {drone_id} on {msg.topic}: {payload}")

        # Salvo i dati in base al topic
        if mqtt.topic_matches_sub(gps_topic, msg.topic):
            gps_data[drone_id] = payload
        elif mqtt.topic_matches_sub(image_processing_topic, msg.topic):
            image_processing_data[drone_id] = payload

        print(f"📥 Updated data: GPS({len(gps_data)}) - Image Processing({len(image_processing_data)})")
        print("GPS Data:", gps_data)
        print("Image Processing Data:", image_processing_data)

        # Calcolo del centro dei droni se ho almeno 3 dati GPS e 3 dati di image processing
        if len(gps_data) == 3 and len(image_processing_data) == 3:
            # Calcolo della media in lat/lng per DRONES_CENTER (con chiavi lat, lng, alt)
            avg_lat = np.mean([gps_data[key]["lat"] for key in gps_data])
            avg_lon = np.mean([gps_data[key]["lng"] for key in gps_data])
            avg_alt = np.mean([gps_data[key]["alt"] for key in gps_data])

            drones_center = {
                "lat": float(avg_lat),
                "lng": float(avg_lon),
                "alt": float(avg_alt),
            }
            print(f"📌 Calculated drones center position (lat/lng): {drones_center}")

            payload_string_drones = json.dumps({
                "timestamp": timestamp,
                "type": "DRONES_CENTER",
                "lat": drones_center["lat"],
                "lng": drones_center["lng"],
                "alt": drones_center["alt"]
            })
            client.publish(publish_drones_center_topic, payload_string_drones)
            print(f"📤 Published to '{publish_drones_center_topic}': {payload_string_drones}")

            # Calcolo della media in coordinate cartesiane (x, y, z) utilizzando (0,0) come riferimento
            lat_ref = 0
            lon_ref = 0

            cartesian_positions = [
                gps_to_cartesian(gps_data[key]["lat"], gps_data[key]["lng"], lat_ref, lon_ref)
                for key in gps_data
            ]
            cartesian_positions = np.array(cartesian_positions)

            avg_x = np.mean(cartesian_positions[:, 0])
            avg_y = np.mean(cartesian_positions[:, 1])
            # Utilizzo la stessa altitudine media calcolata sopra
            drones_center_cartesian = {"x": float(avg_x), "y": float(avg_y), "z": float(avg_alt)}
            print(f"📌 Calculated drones center position (cartesian): {drones_center_cartesian}")

            payload_string_cartesian = json.dumps({
                "timestamp": timestamp,
                "type": "DRONES_CENTER_CARTESIAN",
                "x": drones_center_cartesian["x"],
                "y": drones_center_cartesian["y"],
                "z": drones_center_cartesian["z"]
            })

            client.publish(publish_drones_center_cartesian_topic, payload_string_cartesian)
            print(f"📤 Published to '{publish_drones_center_cartesian_topic}': {payload_string_cartesian}")

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
print("GPS Topic:", gps_topic)

# Connect to MQTT Broker
client.connect(mqtt_broker_host, mqtt_broker_port, 60)

# Start the MQTT loop
client.loop_forever()
