import json
import paho.mqtt.client as mqtt
import yaml
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_manager')))
from data_collector import DataCollector
import time


# Default Values
CONF_FILE_PATH = "system_monitoring_conf.yaml"

# Default Configuration Dictionary
configuration_dict = {
    "broker_ip": "127.0.0.1",
    "broker_port": 1883,
    "target_telemetry_topic": "drone/+/telemetry/env",
    "publish_telemetry_topic": "service/sys_monitoring/env",
    "device_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/location/l0001/device"
}

# Read Configuration from target Configuration File Path
def read_configuration_file():
    global configuration_dict

    with open(CONF_FILE_PATH, 'r') as file:
        configuration_dict = yaml.safe_load(file)

    return configuration_dict

configuration_dict = read_configuration_file()

print("Read Configuration from file ({}): {}".format(CONF_FILE_PATH, configuration_dict))

# MQTT Broker Configuration
mqtt_broker_host = configuration_dict["broker_ip"]
mqtt_broker_port = configuration_dict["broker_port"]
mqtt_topic = configuration_dict["target_telemetry_topic"]
mqtt_publish = configuration_dict["publish_telemetry_topic"]


# HTTP API Configuration
api_url = configuration_dict["device_api_url"]

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):

    if mqtt.topic_matches_sub(mqtt_topic, msg.topic):
        try:

            payload_dict = json.loads(msg.payload.decode())
            device_id = msg.topic.split('/')[1]

            
            device_telemetry_payload = {
                "data_type": payload_dict["type"],
                "value": payload_dict["value"],
                #"timestamp": payload_dict["timestamp"]
            }

            data_collector.add_last_device_data(device_id, device_telemetry_payload)
            print(len(data_collector.get_last_device_data()))

            if len(data_collector.get_last_device_data()) == 2:
                data = data_collector.get_last_device_data()
                values = [float(d['value'].split()[0]) for d in data]
                avg_value = sum(values) / len(values)
                avg_telemetry_payload = {
                    "data_type": data[0]['data_type'],
                    "value": avg_value,
                    "timestamp": time.time()
                }
                print(data)
                print(avg_telemetry_payload)
                client.publish(mqtt_publish, json.dumps(avg_telemetry_payload))
                data_collector.delete_last_device_data()

        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")

#Create Data collector
data_collector = DataCollector()

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(mqtt_broker_host, mqtt_broker_port, 60)

# Start the MQTT loop
client.loop_forever()
