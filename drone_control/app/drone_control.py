import json
import paho.mqtt.client as mqtt
import yaml
import os
import sys
import numpy as np
import time
import math
 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'data_manager')))
from data_manager.data_collector import DataCollector
 
CONF_FILE_PATH = "drone_control_conf.yaml"
 
configuration_dict = {
    "broker_ip": "127.0.0.1",
    "broker_port": 1883,
    "target_cartesian_topic": "drone/+/telemetry/cartesian",
    "target_drone_center_cartesian_topic": "service/flock_localization/drones_center_cartesian",
    "target_points_list": "service/control/track_points",
    "device_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/location/l0001/device",
    "control_input_topic": "drone/{}/control_input"
}
 
if os.path.exists(CONF_FILE_PATH):
    with open(CONF_FILE_PATH, 'r') as file:
        configuration_dict.update(yaml.safe_load(file))
 
print(f"Configurazione: {configuration_dict}")
 
mqtt_broker_host = configuration_dict["broker_ip"]
mqtt_broker_port = configuration_dict["broker_port"]
mqtt_topic_points_list = configuration_dict["target_points_list"]
mqtt_topic_cartesian = configuration_dict["target_cartesian_topic"]
mqtt_topic_drone_center_cartesian = configuration_dict["target_drone_center_cartesian_topic"]
mqtt_topic_control_input = configuration_dict["control_input_topic"]
api_url = configuration_dict["device_api_url"]
data_collector = DataCollector()
 
 
def on_connect(client, userdata, flags, rc):
    print(f"Connesso al broker MQTT con codice: {rc}")
    client.subscribe(mqtt_topic_drone_center_cartesian)
    client.subscribe(mqtt_topic_cartesian)
    client.subscribe(mqtt_topic_points_list)
 
 
def on_message(client, userdata, msg):
    try:
        payload_dict = json.loads(msg.payload.decode())
        if not isinstance(payload_dict, dict):
            raise ValueError("Il payload ricevuto non è un dizionario valido.")
 
        if mqtt.topic_matches_sub(mqtt_topic_cartesian, msg.topic) or mqtt.topic_matches_sub(mqtt_topic_drone_center_cartesian,
                                                                                       msg.topic):
            print(f"📥 Messaggio ricevuto: {msg.topic} -> {payload_dict}")
            device_id = msg.topic.split('/')[1]
            drone_gps_payload = {
                "device_id": device_id,
                "data_type": payload_dict["type"],
                "x": payload_dict["x"],
                "y": payload_dict["y"],
                "z": payload_dict["z"]
            }
            data_collector.add_last_device_data(device_id, drone_gps_payload)
            print(f"Dati aggiornati: {data_collector.get_last_device_data()}")
 
        elif mqtt.topic_matches_sub(mqtt_topic_points_list, msg.topic):
            points_list_payload = {
                "mission_type": payload_dict.get("mission_type", ""),
                "mission_points": payload_dict.get("mission_points", [])
            }
            data_collector.add_points_list(points_list_payload)
    except json.JSONDecodeError:
        print(f"❌ Errore nel decodificare il payload JSON dal topic {msg.topic}")
    except Exception as e:
        print(f"❌ Errore generico nella gestione del messaggio: {e}")
 
    if len(data_collector.get_last_device_data()) == 4 and data_collector.get_points_list():
        time.sleep(0.2)
        process_control(client)
        data_collector.delete_last_device_data()
 
 
def process_control(client):
    data = data_collector.get_last_device_data()
    points_list = data_collector.get_points_list()["mission_points"]
    if not points_list:
        print("Nessun punto di missione disponibile.")
        return
 
    # Il punto di missione rappresenta il centro desiderato della formazione.
    mission_point = np.array(points_list[0])
    print(f"Punto di missione: {mission_point}")
 
    # Recupero il centro attuale della formazione dai dati DRONES_CENTER_CARTESIAN
    center_position = next(
        ([d["x"], d["y"], d["z"]] for d in data if d["data_type"] == "DRONES_CENTER_CARTESIAN"),
        [0, 0, 0]
    )
    center_position = np.array(center_position)
    print(f"Centro attuale: {center_position}")
 
    # Se il centro attuale è sufficientemente vicino al punto di missione, rimuovo il punto
    if np.linalg.norm(mission_point - center_position) < 2:
        print("Il centro è vicino al punto di missione, rimuovo il punto dalla lista.")
        data_collector.remove_point()
        if not data_collector.get_points_list()["mission_points"]:
            print("Missione completata")
            #client.disconnect()
            return
 
    # Calcolo del controllo di tracking del centro (u_center)
    k_center = 0.4
    u_center = k_center * (mission_point - center_position)
    print(f"Controllo tracking centro (u_center): {u_center}")
 
    # Preleviamo le posizioni correnti dei droni (data_type == DRONE_POSITION)
    drone_positions = {
        d["device_id"]: np.array([d["x"], d["y"], d["z"]])
        for d in data if d["data_type"] == "DRONE_POSITION"
    }
    drone_ids = sorted(drone_positions.keys())
    if len(drone_ids) != 3:
        print("Numero di droni diverso da 3, impossibile formare un triangolo equilatero.")
        return
 
    # Calcolo degli offset per un triangolo equilatero di lato 5 (nel piano x-z, y = 0)
    s = 5.0
    R = s / math.sqrt(3)  # Raggio circoscritto ~2.88675
    # Assegno gli offset in base all'ordine (per esempio: drone1 in alto, drone2 a sinistra, drone3 a destra)
    desired_offsets = {
        drone_ids[0]: np.array([0.0, 0.0, R]),
        drone_ids[1]: np.array([-s / 2, 0.0, -R / 2]),
        drone_ids[2]: np.array([s / 2, 0.0, -R / 2])
    }
 
    # Guadagno per il controllo posizione individuale
    k_pos = 0.4
    for drone_id, current_pos in drone_positions.items():
        # Calcolo della posizione desiderata per la formazione (solo con l'offset, senza il tracking)
        desired_pos_formation = center_position + desired_offsets[drone_id]
        # Calcolo del controllo di formazione (u_formation) basato sull'errore tra posizione desiderata (formation) e posizione attuale
        u_formation = k_pos * (desired_pos_formation - current_pos)
        # Il controllo totale è la somma di u_center (che sposta il centro) e u_formation (che regola la formazione)
        u_total = u_center + u_formation
 
        print(f"Control input per {drone_id}: {u_total}, u_center: {u_center}, u_formation: {u_formation}")
 
        control_message = {
            "data_type": "CONTROL_INPUT",
            "u_x": float(u_total[0]),
            "u_y": float(u_total[1]),
            "u_z": float(u_total[2])
        }
        topic = mqtt_topic_control_input.format(drone_id)
        client.publish(topic, json.dumps(control_message))
 
 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker_host, mqtt_broker_port, 60)
client.loop_forever()