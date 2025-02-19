from flask import Flask
from flask_restful import Api
from persistence.data_manager import DataManager
from resources.telemetry_data_resource import TelemetryDataResource
from resources.mission_points_resource import MissionPoints
from resources.flock_center_resource import FlockCenterResource
from resources.drones_center_resource import DronesCenterResource
from resources.environment_resource import EnvironmentResource
import yaml

# Default Values
CONF_FILE_PATH = "conf.yaml"
DEFAULT_ENDPOINT_PREFIX = "/api/v1/iot/inventory"

# Default Configuration Dictionary
configuration_dict = {
    "rest":{
        "api_prefix": DEFAULT_ENDPOINT_PREFIX, 
        "host": "0.0.0.0",
        "port": 7070
    },
    "gateway":{
        "host": "127.0.0.1",
        "port": 7072,
        "gateway_prefix" : "/gateway",
        "control_endpoint" : "/controls/mission-points"
    }
}

# Read Configuration from target Configuration File Path
def read_configuration_file():
    global configuration_dict

    with open(CONF_FILE_PATH, 'r') as file:
        configuration_dict = yaml.safe_load(file)

    return configuration_dict

# Read Configuration file
configuration_dict = read_configuration_file()

print("Read Configuration from file ({}): {}".format(CONF_FILE_PATH, configuration_dict))

gateway_host = configuration_dict['gateway']['host']
gateway_prefix = configuration_dict['gateway']['gateway_prefix']
gateway_port = configuration_dict['gateway']['port']
gateway_endpoint = configuration_dict['gateway']['control_endpoint']

#control_input_url = configuration_dict['gateway']['gateway_prefix']+configuration_dict['gateway']['control_endpoint']

control_input_url = "http://"+gateway_host+":"+str(gateway_port)+gateway_prefix+gateway_endpoint

app = Flask(__name__)
api = Api(app)

print("Starting HTTP RESTful API Server ...")

data_manager = DataManager()

# Add Resources and Endpoints
api.add_resource(TelemetryDataResource, configuration_dict['rest']['api_prefix'] + '/device/<string:device_id>/telemetry',
                      resource_class_kwargs={'data_manager': data_manager},
                      endpoint="device_telemetry_data",
                      methods=['GET', 'POST'])


api.add_resource(MissionPoints, configuration_dict['rest']['api_prefix'] + '/controls/mission-points',
                 resource_class_kwargs={'data_manager': data_manager,
                                        'control_input_url':control_input_url},
                 endpoint="mission-points",
                 methods=['PUT', 'GET'])

api.add_resource(FlockCenterResource, configuration_dict['rest']['api_prefix'] + '/position/flock_center',
                      resource_class_kwargs={'data_manager': data_manager},
                      endpoint="flock_center_telemetry_data",
                      methods=['GET', 'POST'])

api.add_resource(DronesCenterResource, configuration_dict['rest']['api_prefix'] + '/position/drones_center',
                      resource_class_kwargs={'data_manager': data_manager},
                      endpoint="drones_center_telemetry_data",
                      methods=['GET', 'POST'])

api.add_resource(EnvironmentResource, configuration_dict['rest']['api_prefix'] + '/environment',
                      resource_class_kwargs={'data_manager': data_manager},
                      endpoint="environmental_data",
                      methods=['GET', 'PUT'])

if __name__ == '__main__':

    # Run the Flask Application
    app.run(host=configuration_dict['rest']['host'], port=configuration_dict['rest']['port'])  # run our Flask app