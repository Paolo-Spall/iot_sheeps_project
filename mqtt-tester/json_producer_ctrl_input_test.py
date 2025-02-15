# For this example we rely on the Paho MQTT Library for Python
# You can install it through the following command: pip install paho-mqtt

from model.environmental_sensor import EnvironmentalSensor
from model.gps_sensor import GPSSensor  # Aggiunto il sensore GPS
from model.image_processing_system import ImageProcessingSensor  # Aggiunto il nuovo sensore
from model.message_descriptor import MessageDescriptor
import paho.mqtt.client as mqtt
import time
import json


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# Configuration variables
device_id = "d0001"
client_id = "client-ctrl_input-Test-Producer"
broker_ip = "127.0.0.1"
broker_port = 1883
default_topic_control_input = f"drone/{device_id}/control_input"# Nuovo topic per il sensore di elaborazione immagine
message_limit = 1000

mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = on_connect

print("Connecting to " + broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()


for message_id in range(message_limit):


    # Creazione del payload per i dati di controllo

    payload_string_environment = json.dumps({
        "timestamp":int(time.time()),
        "type":"CONTROL_INPUT_TEST",
        "control_input": [0.118, 0.118, 0.0]
        }
    )


    # Pubblica i dati
    infot_environment = mqtt_client.publish(default_topic_control_input, payload_string_environment)
    infot_environment.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {default_topic_control_input} Payload: {payload_string_environment}")


    time.sleep(5)

mqtt_client.loop_stop()
