import paho.mqtt.client as mqtt
from model.message_descriptor import MessageDescriptor
import json

# Configuration variables
client_id = "clientId0001-Consumer"
broker_ip = "127.0.0.1"
broker_port = 1883
# Filtri aggiornati per localizazione dei droni e del gregge
target_topic_drones_center_filter = "service/flock_localization/drones_center"
target_topic_flock_center_filter = "service/flock_localization/flock_center"
target_topic_drones_center_cartesian_filter = "service/flock_localization/drones_center_cartesian"
message_limit = 1000

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Iscrizione ai topic per i dati
    mqtt_client.subscribe(target_topic_drones_center_filter)
    mqtt_client.subscribe(target_topic_flock_center_filter)
    mqtt_client.subscribe(target_topic_drones_center_cartesian_filter)
    print(f"Subscribed to: {target_topic_drones_center_filter}, {target_topic_flock_center_filter} and {target_topic_drones_center_cartesian_filter}")

# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    message_payload = str(message.payload.decode("utf-8"))
    # Se si utilizza MessageDescriptor:
    # message_descriptor = MessageDescriptor(**json.loads(message_payload))
    
    topic_matched = False  # Flag per controllare se il messaggio corrisponde a un filtro conosciuto

    if mqtt.topic_matches_sub(target_topic_drones_center_filter, message.topic):
        print("📥 Message received for Localization service (Drones Center):")
        print(message_payload)
        topic_matched = True

    if mqtt.topic_matches_sub(target_topic_flock_center_filter, message.topic):
        print("📥 Message received for Localization service (Flock Center):")
        print(message_payload)
        topic_matched = True

    if mqtt.topic_matches_sub(target_topic_drones_center_cartesian_filter, message.topic):
        print("📥 Message received for Localization service (Drones Center Cartesian):")
        print(message_payload)
        topic_matched = True

    if not topic_matched:
        print(f"❌ Message topic '{message.topic}' does not match any known filter")

# Create a new MQTT Client
mqtt_client = mqtt.Client(client_id)

# Attach Paho OnMessage and OnConnect Callback Methods
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

# Connect to the target MQTT Broker
mqtt_client.connect(broker_ip, broker_port)

# Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
mqtt_client.loop_forever()
