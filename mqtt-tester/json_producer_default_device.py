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
device_id = "d0001"
client_id = "clientId0001-Producer"
broker_ip = "127.0.0.1"
broker_port = 1883
default_topic_environment = f"device/{device_id}/environment"
default_topic_gps = f"device/{device_id}/gps"  # Nuovo topic per il GPS
default_topic_image_processing = f"device/{device_id}/image_processing"  # Nuovo topic per il sensore di elaborazione immagine
message_limit = 1000

mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = on_connect

print("Connecting to " + broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

# Crea i sensori
environmental_sensor = EnvironmentalSensor()
gps_sensor = GPSSensor()  # Creazione del sensore GPS
image_processing_sensor = ImageProcessingSensor()  # Creazione del sensore di elaborazione immagine

for message_id in range(message_limit):
    environmental_sensor.measure_environment()  # Acquisisce nuovi dati ambientali
    sensor_data_environment = environmental_sensor.get_data()

    gps_sensor.measure_position()  # Acquisisce nuove coordinate GPS
    sensor_data_gps = {
        'x': gps_sensor.x_position,
        'y': gps_sensor.y_position,
        'z': gps_sensor.z_position,
        'timestamp': gps_sensor.timestamp
    }

    image_processing_sensor.measure_distance()  # Acquisisce la distanza dal centro del gregge
    sensor_data_image_processing = {
        'distance': image_processing_sensor.distance_to_flock_center,
        'unit': image_processing_sensor.unit_of_measurement,
        'timestamp': image_processing_sensor.timestamp
    }

    # Creazione del payload per i dati ambientali
    payload_string_environment = MessageDescriptor(
        int(time.time()),
        "ENVIRONMENTAL_SENSOR",
        sensor_data_environment
    ).to_json()

    # Creazione del payload per i dati GPS
    payload_string_gps = MessageDescriptor(
        int(time.time()),
        "GPS_SENSOR",
        sensor_data_gps
    ).to_json()

    # Creazione del payload per i dati di elaborazione immagine
    payload_string_image_processing = MessageDescriptor(
        int(time.time()),
        "IMAGE_PROCESSING_SENSOR",
        sensor_data_image_processing
    ).to_json()

    # Pubblica i dati
    infot_environment = mqtt_client.publish(default_topic_environment, payload_string_environment)
    infot_environment.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {default_topic_environment} Payload: {payload_string_environment}")

    infot_gps = mqtt_client.publish(default_topic_gps, payload_string_gps)
    infot_gps.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {default_topic_gps} Payload: {payload_string_gps}")

    infot_image_processing = mqtt_client.publish(default_topic_image_processing, payload_string_image_processing)
    infot_image_processing.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {default_topic_image_processing} Payload: {payload_string_image_processing}")

    time.sleep(5)

mqtt_client.loop_stop()
