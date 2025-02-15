import paho.mqtt.client as mqtt
from model.message_descriptor import MessageDescriptor
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Iscrizione ai topic per i dati ambientali, GPS e di elaborazione immagine
    mqtt_client.subscribe(target_topic_environment_filter)  
  # Iscrizione al topic del sensore di elaborazione immagine
    print(f"Subscribed to: {target_topic_environment_filter}")

# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    message_payload = str(message.payload.decode("utf-8"))
    #message_descriptor = MessageDescriptor(**json.loads(message_payload))

    if mqtt.topic_matches_sub(target_topic_environment_filter, message.topic):
        print("Message received for Environment Microservice:")
        #print(message_descriptor.to_json())
        print(message_payload)
    else:
        print("MEssage topic does not match the target filter")

# Configuration variables
client_id = "clientId0001-Consumer"
broker_ip = "127.0.0.1"
broker_port = 1883
# Filtri aggiornati per i dati ambientali, GPS e di elaborazione immagine
target_topic_environment_filter = "service/sys_monitoring/env"
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
