import paho.mqtt.client as mqtt
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Iscrizione ai topic per i dati ambientali, GPS e di elaborazione immagine
    mqtt_client.subscribe(target_topic_track_points)
# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    message_payload = str(message.payload.decode("utf-8"))

    # Gestione dei dati del sensore ambientale
    if mqtt.topic_matches_sub( target_topic_track_points, message.topic):
        print(f"Received point list: {message.topic} ")
        print(f"Payload: {message_payload}")

# Configuration variables
client_id = "clientId0001-Consumer"
broker_ip = "127.0.0.1"
broker_port = 1883
# Filtri aggiornati per i dati ambientali, GPS e di elaborazione immagine
target_topic_track_points = "service/control/track_points"
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
