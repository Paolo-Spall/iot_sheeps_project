# For this example we rely on the Paho MQTT Library for Python
# You can install it through the following command: pip install paho-mqtt

from model.environmental_sensor import EnvironmentalSensor
from model.gps_sensor import GPSSensor  # Aggiunto il sensore GPS
from model.image_processing_system import ImageProcessingSensor  # Aggiunto il nuovo sensore
from model.env_message_descriptor import MessageDescriptor
import paho.mqtt.client as mqtt
import time


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# Configuration variables
device_id = "d0009"
client_id = "clientId0009-Producer"
broker_ip = "127.0.0.1"
broker_port = 1883
default_topic_environment = f"drone/{device_id}/telemetry/env"# Nuovo topic per il sensore di elaborazione immagine
message_limit = 1000

mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = on_connect

print("Connecting to " + broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

# Crea i sensori
environmental_sensor = EnvironmentalSensor()

for message_id in range(message_limit):
    environmental_sensor.measure_environment()  # Acquisisce nuovi dati ambientali
    sensor_data_environment = environmental_sensor.get_data()


    # Creazione del payload per i dati ambientali
    payload_string_environment = MessageDescriptor(
        int(time.time()),
        "ENVIRONMENTAL_SENSOR",
        sensor_data_environment["temperature value"],
        sensor_data_environment["temperature udm"],
        sensor_data_environment["humidity"],
        sensor_data_environment["rain probability"]
    ).to_json()


    # Pubblica i dati
    infot_environment = mqtt_client.publish(default_topic_environment, payload_string_environment)
    infot_environment.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {default_topic_environment} Payload: {payload_string_environment}")


    time.sleep(5)

mqtt_client.loop_stop()
