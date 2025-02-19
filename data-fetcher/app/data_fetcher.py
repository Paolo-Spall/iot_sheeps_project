import json
import requests
import paho.mqtt.client as mqtt
import yaml

# Default Values
CONF_FILE_PATH = "fetcher_conf.yaml"

# Default Configuration Dictionary
configuration_dict = {
    "broker_ip": "127.0.0.1",
    "broker_port": 1883,
    "target_telemetry_topic": "service/flock_localization/flock_center",
    "target_telemetry_d_topic": "service/flock_localization/drones_center_gps",
    "target_environment_topic": "service/sys_monitoring/env",
    "target_battery_topic": "drone/+/telemetry/battery",
    "device_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/position/flock_center",
    "drones_center_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/position/drones_center",
    "environment_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/environment",
    "batteries_api_url": "http://127.0.0.1:7070/api/v1/iot/inventory/batteries"
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
mqtt_topic_d = configuration_dict["target_telemetry_d_topic"]
mqtt_topic_env = configuration_dict["target_environment_topic"]
mqtt_topic_batteries = configuration_dict["target_battery_topic"]


# HTTP API Configuration
api_url = configuration_dict["device_api_url"]
drones_center_api_url = configuration_dict["drones_center_api_url"]
env_api_url = configuration_dict["environment_api_url"]
bat_api_url = configuration_dict["batteries_api_url"]

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(mqtt_topic)
    client.subscribe(mqtt_topic_d)
    client.subscribe(mqtt_topic_env)
    client.subscribe(mqtt_topic_batteries)

def on_message(client, userdata, msg):

    if mqtt.topic_matches_sub(mqtt_topic, msg.topic):
        try:

            payload_dict = json.loads(msg.payload.decode())
            device_id = msg.topic.split('/')[1]

            # Check if the device exists in the inventory
            telemetry_device_url = f"{api_url}"

            print(f'Flock center telemetry: {device_id} Sending HTTP POST Request to: {telemetry_device_url}')

            device_telemetry_payload = {
                "timestamp": payload_dict["timestamp"],
                "x": payload_dict["x"],
                "y": payload_dict["y"]
            }

            create_device_response = requests.post(telemetry_device_url, json=device_telemetry_payload)

            if create_device_response.status_code == 201:
                print(f"Device Telemetry {device_id} registered successfully.")
            else:
                print(f"Failed to register telemetry {device_id}. Status code: {create_device_response.status_code} Response: {create_device_response.text}")

        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")

    if mqtt.topic_matches_sub(mqtt_topic_d, msg.topic):
        try:

            payload_dict = json.loads(msg.payload.decode())
            device_id = msg.topic.split('/')[1]

            # Check if the device exists in the inventory
            telemetry_device_url = f"{drones_center_api_url}"

            print(f'Drones center telemetry: {device_id} Sending HTTP POST Request to: {telemetry_device_url}')

            device_telemetry_payload = {
                "timestamp": payload_dict["timestamp"],
                "lat": payload_dict["lat"],
                "lng": payload_dict["lng"],
                "alt": payload_dict["alt"]
            }

            create_device_response = requests.post(telemetry_device_url, json=device_telemetry_payload)

            if create_device_response.status_code == 201:
                print(f"Device Telemetry {device_id} registered successfully.")
            else:
                print(f"Failed to register telemetry {device_id}. Status code: {create_device_response.status_code} Response: {create_device_response.text}")

        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")

    if mqtt.topic_matches_sub(mqtt_topic_env, msg.topic):
        try:

            payload_dict = json.loads(msg.payload.decode())
            device_id = msg.topic.split('/')[1]

            # Check if the device exists in the inventory
            telemetry_device_url = f"{env_api_url}"

            print(f'Environmental data: {device_id} Sending HTTP POST Request to: {telemetry_device_url}')

            device_telemetry_payload = {
                "timestamp": payload_dict["timestamp"],
                "temperature_value": payload_dict["temperature_value"],
                "humidity": payload_dict["humidity"],
                "rain_probability": payload_dict["rain_probability"]
            }

            create_device_response = requests.put(telemetry_device_url, json=device_telemetry_payload)

            if create_device_response.status_code == 201:
                print(f"Device Telemetry {device_id} registered successfully.")
            else:
                print(f"Failed to register telemetry {device_id}. Status code: {create_device_response.status_code} Response: {create_device_response.text}")

        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")


# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(mqtt_broker_host, mqtt_broker_port, 60)

# Start the MQTT loop
client.loop_forever()
