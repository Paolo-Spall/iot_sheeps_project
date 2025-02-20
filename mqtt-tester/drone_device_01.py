# For this example we rely on the Paho MQTT Library for Python
# You can install it through the following command: pip install paho-mqtt

from model.drone import Drone
import paho.mqtt.client as mqtt
import time
import json

# Configuration variables
drone_id = "d0001"
client_id = "drone-d0001-Subscriber-Producer"
broker_ip = "127.0.0.1"
broker_port = 1883
default_topic_publish = f"drone/{drone_id}/"
#message_limit = 1000

topic_info = f"drone/{drone_id}/info"  # Nuovo topic per le informazioni del drone
topic_cartesian_publish = f"drone/{drone_id}/telemetry/cartesian"  # Nuovo topic per il sensore di elaborazione immagine
topic_gps_publish = f"drone/{drone_id}/telemetry/gps"  # Nuovo topic per il GPS
topic_image_processing_publish = f"drone/{drone_id}/telemetry/image_processing"  # Nuovo topic per il sensore di elaborazione immagine
topic_environmental_data_publish = f"drone/{drone_id}/telemetry/environmental_data"  # Nuovo topic per il sensore di elaborazione immagine
topic_control_input_subscribe = f"drone/{drone_id}/control_input"  # Nuovo topic per il sensore di elaborazione immagine

drone = Drone(drone_id)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    dorne_info = json.loads(drone.get_drone_info())
    print(f"Drone {dorne_info['id']} connected to MQTT Broker with result code " + str(rc))  
    print(f"📤 Publishing to topic {topic_info}")
    client.publish(topic_info, drone.get_drone_info(), retain=True)
    client.subscribe(topic_control_input_subscribe)
    client.publish(topic_cartesian_publish, drone.get_drone_position())
    client.publish(topic_gps_publish, drone.get_gps_data())
    client.publish(topic_image_processing_publish, drone.get_image_processing_data())


mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = on_connect

print("Connecting to " + broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)


def on_message(client, userdata, msg):
    if mqtt.topic_matches_sub(topic_control_input_subscribe, msg.topic):

        try:
            payload_dict = json.loads(msg.payload.decode())

            # Stampa la struttura del payload per il debug
            print(f"Payload received- Topic: {msg.topic} - Type: {payload_dict['data_type']}")

            # Se il payload è una lista
            if isinstance(payload_dict, list):
                # Itera sulla lista e estrai le coordinate da ciascun dizionario
                control_input = [
                    [d.get('u_x'), d.get('u_y'), d.get('u_z')] for d in payload_dict if isinstance(d, dict)
                ]
            # Se il payload è un dizionario
            elif isinstance(payload_dict, dict):
                # Estrai direttamente le coordinate dal dizionario
                control_input = [payload_dict.get('u_x'), payload_dict.get('u_y'), payload_dict.get('u_z')]
            else:
                raise ValueError("Invalid payload structure")
           

        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")

        drone.update_position(control_input)
        drone.read_sensors()

        try:
            print("📤 Publishing telemetry")
            client.publish(topic_cartesian_publish, drone.get_drone_position())
            #print(f"📤 Publishing to topic {topic_gps_publish}")
            #client.publish(topic_gps_publish, drone.get_gps_data())
            #print(f"📤 Publishing to topic {topic_image_processing_publish}")
            client.publish(topic_image_processing_publish, drone.get_image_processing_data())
            #print(f"📤 Publishing to topic {topic_environmental_data_publish}")
            client.publish(topic_environmental_data_publish, drone.get_environmental_data())

        except Exception as e:
            print(f"Error publishing MQTT message: {str(e)}")


# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(broker_ip, broker_port, 60)

# Start the MQTT loop
print("Starting MQTT loop...")
client.loop_forever()

