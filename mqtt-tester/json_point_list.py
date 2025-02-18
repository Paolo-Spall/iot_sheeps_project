import paho.mqtt.client as mqtt
import json

# Configurazione del broker MQTT
broker_ip = "127.0.0.1"  # IP del broker MQTT
broker_port = 1883  # Porta MQTT (default 1883)
topic_publish = "service/control/track_points"

# Messaggio da inviare
mission_data = {
    "mission_type": "grazing",
    "mission_points": [
        [50, 0, 20], [100, 0, 20], [100, -50, 20], [100, -100, 20],
        [50, -100, 20], [0, -100, 20], [0, -50, 20], [0, 0, 20]
    ]
}

# Callback per la connessione
def on_connect(client, userdata, flags, rc):
    print("Connesso al broker MQTT con codice:", rc)
    client.publish(topic_publish, json.dumps(mission_data))
    print(f"Messaggio inviato su {topic_publish}: {mission_data}")
    client.disconnect()

# Creazione del client MQTT
client = mqtt.Client()
client.on_connect = on_connect

# Connessione al broker
client.connect(broker_ip, broker_port, 60)

# Avvio del loop per gestire la connessione
client.loop_forever()
