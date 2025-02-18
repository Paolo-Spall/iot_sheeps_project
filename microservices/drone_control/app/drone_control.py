import json
import paho.mqtt.client as mqtt
import yaml
import os
import sys
import numpy as np
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'data_manager')))
from data_collector import DataCollector

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

    center_position = next(
        ([d["x"], d["y"], d["z"]] for d in data if d["data_type"] == "DRONES_CENTER_CARTESIAN"),
        [0, 0, 0]
    )
    print(f"Centro attuale: {center_position}")
    print(f"Punto di missione: {points_list[0]}")

    np_points_list = np.array(points_list)
    np_center_position = np.array(center_position)

    if np.linalg.norm(np_points_list[0] - np_center_position) < 2:
        data_collector.remove_point()
        if not data_collector.get_points_list()["mission_points"]:
            print("Missione completata")
            client.disconnect()
            return

    try:
        k = 0.4
        u_c = np.array([k * (np_points_list[0][i] - center_position[i]) for i in range(3)])
        print(f"Controllo di tracking: {u_c}")

        desired_distance = 1
        formation_k = 0.2
        drone_positions = {d["device_id"]: [d["x"], d["y"], d["z"]] for d in data if d['data_type'] == 'DRONE_POSITION'}
        u_f = {drone_id: np.zeros(3) for drone_id in drone_positions.keys()}
        drone_ids = list(drone_positions.keys())

        for i in range(len(drone_ids)):
            for j in range(i + 1, len(drone_ids)):
                id_i, id_j = drone_ids[i], drone_ids[j]
                pos_i, pos_j = np.array(drone_positions[id_i]), np.array(drone_positions[id_j])
                distance = np.linalg.norm(pos_j - pos_i)
                error = distance - desired_distance
                if distance > 1e-6:
                    direction = (pos_j - pos_i) / distance
                    correction = formation_k * error * direction
                    u_f[id_i] += correction
                    u_f[id_j] -= correction

        for drone_id, position in drone_positions.items():
            u_c_drone = np.array([k * (np_points_list[0][i] - position[i]) for i in range(3)])
            u_total = u_c_drone + u_f[drone_id]
            print(f"Control input per {drone_id}: {u_total}")
            control_message = {
                "data_type": "CONTROL_INPUT",
                "u_x": float(u_total[0]),
                "u_y": float(u_total[1]),
                "u_z": float(u_total[2])
            }
            topic = mqtt_topic_control_input.format(drone_id)
            client.publish(topic, json.dumps(control_message))
    except Exception as e:
        print(f"Errore nel calcolo del controllo: {str(e)}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker_host, mqtt_broker_port, 60)
client.loop_forever()