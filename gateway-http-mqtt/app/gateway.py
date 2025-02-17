#/usr/bin/python3

from flask import Flask, request
import paho.mqtt.client as mqtt
import yaml
import json
import time

CONF_FILE_PATH = "gateway_conf.yaml"
DEFAULT_REST_PREFIX = "/gateway/"
#"/gateway/controls/mission-points"
CONTROL_ENDPOINT = "controls/mission-points"

app = Flask(__name__)

configuration_dict = {
    "mqtt": {
        "client_id": "gateway001",
        "broker_ip": "127.0.0.1",
        "broker_port": 1883,
        "topic": "service/control/track_points"},
    "http": {
        "host": "127.0.0.1",
        "port": 7072,
        "rest_prefix": DEFAULT_REST_PREFIX}
}

# Read Configuration from target Configuration File Path
def read_configuration_file():
    global configuration_dict

    with open(CONF_FILE_PATH, 'r') as file:
        configuration_dict = yaml.safe_load(file)

    return configuration_dict

# Read Configuration file
configuration_dict = read_configuration_file()

# REST Configuration
rest_prefix = configuration_dict['http']['rest_prefix']
mission_points_endpoint = rest_prefix + CONTROL_ENDPOINT

# MQTT Configuration
client_id = configuration_dict['mqtt']['client_id']
broker_ip = configuration_dict['mqtt']['broker_ip']
broker_port = configuration_dict['mqtt']['broker_port']
mqtt_topic = configuration_dict['mqtt']['topic']

# rule to fetch mission points requests to mqtt
@app.route(mission_points_endpoint, methods=['PUT'])
def fetch_mission_points():

    print("Received Mission Points Request")
    # Get the mission points from the request
    try:
        data = request.json
        type = data['mission_type']
        points = data['mission_points']
    except Exception as e:
        print(e)
        return {"error": "Invalid request data"}, 400
    
    payload = json.dumps({"mission_type": type, "mission_points": points})
    # Send the mission points to the MQTT Broker

    #try:
    mqtt_client.publish(mqtt_topic, payload)
    infot_environment = mqtt_client.publish(mqtt_topic, payload)
    infot_environment.wait_for_publish()
    print(f"Message Sent - Topic: {mqtt_topic} Payload: {payload}")

    # except Exception as e:
    #     print(e)
    #     return {"error": "Error sending mission points to MQTT Broker"}, 500
    return {"message": "Mission points sent to MQTT Broker"}, 200

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    

if __name__ == '__main__':

    mqtt_client = mqtt.Client(client_id)
    mqtt_client.on_connect = on_connect

    print("Connecting to " + broker_ip + " port: " + str(broker_port))
    mqtt_client.connect(broker_ip, broker_port)

    mqtt_client.loop_start()

    time.sleep(5)
    # Run the Flask Application
    app.run(host=configuration_dict['http']['host'], 
            port=configuration_dict['http']['port'])  # run our Flask app
