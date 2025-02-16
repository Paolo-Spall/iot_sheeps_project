import paho.mqtt.client as mqtt
from model.message_descriptor import MessageDescriptor
import json

# Configuration variables
client_id = "clientId0001-Consumer"
broker_ip = "127.0.0.1"
broker_port = 1883
# Filtri aggiornati per localizazione dei droni e del gregge
target_topic_drones_center_filter = "service/flock_localization/drones_center"
target_topic_flock_center_filter="service/flock_localization/flock_center"
message_limit = 1000


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Iscrizione ai topic per i dati ambientali, GPS e di elaborazione immagine
    mqtt_client.subscribe(target_topic_drones_center_filter)
    mqtt_client.subscribe(target_topic_flock_center_filter)
  # Iscrizione al topic del sensore di elaborazione immagine
    print(f"Subscribed to: {target_topic_drones_center_filter} and {target_topic_flock_center_filter}")

# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    message_payload = str(message.payload.decode("utf-8"))
    #message_descriptor = MessageDescriptor(**json.loads(message_payload))

    
    if mqtt.topic_matches_sub(target_topic_drones_center_filter, message.topic):
        print("📥 Message received for Localization service (Drones Center):")
        print(message_payload)
        topic_matched = True  # Segnalo che il messaggio è stato gestito da un filtro

    if mqtt.topic_matches_sub(target_topic_flock_center_filter, message.topic):
        print("📥 Message received for Localization service (Flock Center):")
        print(message_payload)
        topic_matched = True  # Segnalo che il mess