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
    "publish_notification_topic": "notification",
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
mqtt_notification = configuration_dict["publish_notification_topic"]


# HTTP API Configuration
api_url = configuration_dict["device_api_url"]

# Telemetry value
telemetry_value = ["temperature_value", "humidity", "rain_probability"]

# Define the thresholds
TEMP_MIN, TEMP_MAX = 0, 35
HUMIDITY_MAX = 85
RAIN_PROB_MAX = 4.1


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
                "temperature_value": payload_dict["temperature_value"],
                "temperature_udm": payload_dict["temperature_udm"],
                "humidity": payload_dict["humidity_value"],
                "rain_probability": payload_dict["rain_probability"],
            }

            data_collector.add_last_device_data(device_id, device_telemetry_payload)
            print(len(data_collector.get_last_device_data()))

            if len(data_collector.get_last_device_data()) == 3:
                avg_value = []
                for i in telemetry_value:
                    data = data_collector.get_last_device_data()
                    values = [float(d[i]) for d in data]
                    avg_value.append(sum(values) / len(values))
                avg_telemetry_payload = {
                    "data_type": data[0]['data_type'],
                    "temperature_value": round(float(avg_value[0]), 1),
                    "temperature_type": data[0]['temperature_udm'],
                    "humidity": round(float(avg_value[1]), 1),
                    "rain_probability": int(avg_value[2]),
                    "timestamp": int(time.time())
                }

                print(data)
                print(avg_telemetry_payload)
                client.publish(mqtt_publish, json.dumps(avg_telemetry_payload))
                data_collector.delete_last_device_data()
                notification_service(client,avg_value,data)



        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")

def notification_service(client,avg_value,data):
    alerts = []
    payload = {}
    if avg_value[0] < TEMP_MIN:
        alerts.append(f"Temperature too low: {avg_value[0]:.1f}°C")  # Add alert if temp is too low
        payload["temperature_value"] = round(avg_value[0], 1)  # Add temperature value to payload
    elif avg_value[0] > TEMP_MAX:
        alerts.append(f"Temperature too high: {avg_value[0]:.1f}°C")  # Add alert if temp is too high
        payload["temperature_value"] = round(avg_value[0], 1)  # Add temperature value to payload

    if avg_value[1] > HUMIDITY_MAX:
        alerts.append(f"Humidity too high: {avg_value[1]:.1f}%")  # Add alert if humidity is too high
        payload["humidity"] = round(avg_value[1], 1)  # Add humidity value to payload

    if avg_value[2] > RAIN_PROB_MAX:
        alerts.append(f"High rain probability: {avg_value[2]:.1f}")  # Add alert if rain probability is too high
        payload["rain_probability"] = round(avg_value[2], 1)  # Add rain probability value to payload

    avg_telemetry_payload = {
        "data_type": data[0]['data_type'],  # Data type (e.g., environmental sensor)
        "timestamp": time.time(),  # Current timestamp
        "alerts": alerts,  # If no alerts, set alerts as None
    }
    #avg_telemetry_payload.update(payload)
    if alerts:
        print(avg_telemetry_payload)
        client.publish(mqtt_notification, json.dumps(avg_telemetry_payload))


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
