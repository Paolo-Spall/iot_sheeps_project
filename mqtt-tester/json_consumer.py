import paho.mqtt.client as mqtt
from model.message_descriptor import MessageDescriptor
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Iscrizione ai topic per i dati ambientali, GPS e di elaborazione immagine
    mqtt_client.subscribe(target_topic_environment_filter)  
    mqtt_client.subscribe(target_topic_gps_filter)
    mqtt_client.subscribe(target_topic_image_processing_filter)  # Iscrizione al topic del sensore di elaborazione immagine
    print(f"Subscribed to: {target_topic_environment_filter}, {target_topic_gps_filter}, and {target_topic_image_processing_filter}")

# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    message_payload = str(message.payload.decode("utf-8"))
    message_descriptor = MessageDescriptor(**json.loads(message_payload))

    # Gestione dei dati del sensore ambientale
    if mqtt.topic_matches_sub( target_topic_environment_filter, message.topic):
        print(f"Received IoT Message: Topic: {message.topic} ")
        print(f"Temperature: {message_descriptor.value} ")
            
    
    # Gestione dei dati del sensore GPS
    elif "gps" in message.topic:
        print(f"Received IoT Message: Topic: {message.topic} "
              f"Timestamp: {message_descriptor.timestamp} "
              f"Type: {message_descriptor.type} "
              f"X Position: {message_descriptor.value['x']} "
              f"Y Position: {message_descriptor.value['y']} "
              f"Z Position: {message_descriptor.value['z']}")
    
    # Gestione dei dati del sensore di elaborazione immagine
    elif "image_processing" in message.topic:
        print(f"Received IoT Message: Topic: {message.topic} "
              f"Timestamp: {message_descriptor.timestamp} "
              f"Type: {message_descriptor.type} "
              f"Distance from Center of Flock: {message_descriptor.value['distance']} "
              f"Unit: {message_descriptor.value['unit']}")

# Configuration variables
client_id = "clientId0002-Consumer"
broker_ip = "127.0.0.1"
broker_port = 1883
# Filtri aggiornati per i dati ambientali, GPS e di elaborazione immagine
target_topic_environment_filter = "drone/+/telemetry/env"
target_topic_gps_filter = "device/+/gps"
target_topic_image_processing_filter = "device/+/image_processing"  # Nuovo filtro per il sensore di elaborazione immagine
message_limit = 1000

# Create a new MQTT Client
mqtt_client = mqtt.Client(client_id)

# Attach Paho OnMessage Callback Method
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

# Connect to the target MQTT Broker
mqtt_client.connect(broker_ip, broker_port)

# Blocking call that processes network traffic, dispatches callbacks, and
# handles reconnecting. This method will run forever.
mqtt_client.loop_forever()
