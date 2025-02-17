# For this example we rely on the Paho MQTT Library for Python
# You can install it through the following command: pip install paho-mqtt

from model.drone import Drone
import paho.mqtt.client as mqtt
import time
import json



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# Configuration variables
drone_id = "d0004"
client_id = "drone-d0004-Subscriber-Producer"
broker_ip = "127.0.0.1"
broker_port = 1883
default_topic_publish = f"drone/{drone_id}/"

topic_gps_publish = "service/flock_localization/drones_center_cartesian"  # Nuovo topic per il GPS
topic_image_processing_publish = f"drone/{drone_id}/telemetry/image_processing"  # Nuovo topic per il sensore di elaborazione immagine

topic_control_input_subscribe = f"drone/{drone_id}/control_input"# Nuovo topic per il sensore di elaborazione immagine

drone = Drone(drone_id)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(topic_control_input_subscribe)
    client.publish(topic_gps_publish, drone.get_drone_center_position())

def on_message(client, userdata, msg):

    if mqtt.topic_matches_sub(topic_control_input_subscribe, msg.topic):
        #try:

        payload_dict = json.loads(msg.payload.decode())
        control_input = payload_dict['control_input']
        print(f"Received control input: {control_input} - type: {type(control_input)}")

        #except Exception as e:
        #print(f"Error processing MQTT message: {str(e)}")
    
        drone.update_position(control_input)
        drone.read_sensors()

        try:
            client.publish(topic_gps_publish, drone.get_drone_center_position())
            #client.publish(topic_image_processing_publish, drone.get_image_processing_data())
            #client.publish(default_topic_publish, drone.get_environmental_data())

        except Exception as e:
            print(f"Error publishing MQTT message: {str(e)}")

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(broker_ip, broker_port, 60)

# Start the MQTT loop
client.loop_forever()
