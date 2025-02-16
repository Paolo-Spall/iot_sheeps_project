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
    "publish_drones_center_cartesian_topic": "service/flock_localization/drones_center_cartesian",  # Virgola aggiunta qui
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

# Calcolo della posizione del gregge
def calculate_flock_position(timestamp):
    global gps_data, image_processing_data
    if len(gps_data) < 3 or len(image_processing_data) < 3:
        print("⚠️ Non ho abbastanza dati per calcolare la posizione del gregge")
        return

    # Estraggo le coordinate GPS in lat/lon
    lat_lon_positions = np.array([
        [gps_data[key]["value"]["y"], gps_data[key]["value"]["x"]]
        for key in sorted(gps_data.keys())
    ])

    # Prendo il primo drone come riferimento
    lat_ref, lon_ref = lat_lon_positions[0]

    # Converto GPS → (x, y)
    gps_positions = np.array([
        gps_to_cartesian(lat_lon_positions[i][0], lat_lon_positions[i][1], lat_ref, lon_ref)
        for i in range(3)
    ])

    # Estraggo le distanze dal centro del gregge
    distances = np.array([
        image_processing_data[key]["value"]["distance"]
        for key in sorted(image_processing_data.keys())
    ])

    # Trilaterazione (media pesata)
    weights = 1 / distances
    flock_x = np.sum(gps_positions[:, 0] * weights) / np.sum(weights)
    flock_y = np.sum(gps_positions[:, 1] * weights) / np.sum(weights)
    # Calcolo dell'altezza media (z) dai dati GPS
    flock_z = np.mean([gps_data[key]["value"].get("z", 0) for key in gps_data])

    flock_position = {"x": float(flock_x), "y": float(flock_y), "z": float(flock_z)}

    print(f"📌 Calculated flock position: {flock_position}")

    # Pubblica la posizione del gregge
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

        # Controllo del topic
        if mqtt.topic_matches_sub("device/+/gps", msg.topic):
            gps_data[drone_id] = payload
        elif mqtt.topic_matches_sub("device/+/image_processing", msg.topic):
            image_processing_data[drone_id] = payload

        # Pubblicazione del centro dei droni se ho 3 dati GPS
        if len(gps_data) == 3:
            # Calcolo della media in lat/lon
            avg_lat = np.mean([gps_data[key]["value"]["y"] for key in gps_data])
            avg_lon = np.mean([gps_data[key]["value"]["x"] for key in gps_data])
            avg_z = np.mean([gps_data[key]["value"].get("z", 0) for key in gps_data])
            drones_center = {"latitude": float(avg_lat), "longitude": float(avg_lon), "z": float(avg_z)}
            print(f"📌 Calculated drones center position (lat/lon): {drones_center}")
            payload_string_drones = json.dumps({
                "timestamp": timestamp,
                "type": "DRONES_CENTER",
                "value": drones_center
            })
            client.publish(publish_drones_center_topic, payload_string_drones)
            print(f"📤 Published to '{publish_drones_center_topic}': {payload_string_drones}")

            # Calcolo della media in coordinate cartesiane (x,y) utilizzando il primo drone come riferimento
            first_drone = list(gps_data.keys())[0]
            lat_ref = gps_data[first_drone]["value"]["y"]
            lon_ref = gps_data[first_drone]["value"]["x"]
            cartesian_positions = [
                gps_to_cartesian(gps_data[key]["value"]["y"], gps_data[key]["value"]["x"], lat_ref, lon_ref)
                for key in gps_data
            ]
            cartesian_positions = np.array(cartesian_positions)
            avg_x = np.mean(cartesian_positions[:, 0])
            avg_y = np.mean(cartesian_positions[:, 1])
            # avg_z è lo stesso calcolato sopra (l'altezza rimane invariata)
            drones_center_cartesian = {"x": float(avg_x), "y": float(avg_y), "z": float(avg_z)}
            print(f"📌 Calculated drones center position (cartesian): {drones_center_cartesian}")
            payload_string_cartesian = json.dumps({
                "timestamp": timestamp,
                "type": "DRONES_CENTER_CARTESIAN",
                "value": drones_center_cartesian
            })
            client.publish(publish_drones_center_cartesian_topic, payload_string_cartesian)
            print(f"📤 Published to '{publish_drones_center_cartesian_topic}': {payload_string_cartesian}")

        # Se ho tutti i dati (3 GPS + 3 Image Processing), calcolo la posizione del gregge
        if len(gps_data) == 3 and len(image_processing_data) == 3:
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

# Start the MQTT loop
client.loop_forever()
