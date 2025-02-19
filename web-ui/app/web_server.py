import requests
from flask import Flask, request, render_template, jsonify
import os
import yaml
import json
import threading


class WebServer:

    def __init__(self, config_file:str):

        # Server Thread
        self.server_thread = None

        # Save the configuration file
        self.config_file = config_file

        # Get the main communication directory
        main_app_path = ""

        # Construct the file path
        template_dir = os.path.join(main_app_path, 'templates')

        # Set a default configuration
        self.configuration_dict = {
            "web": {
                "host": "0.0.0.0",
                "port": 7071,
                "api_base_url": "http://127.0.0.1:7070/api/v1/iot/inventory"
            }
        }

        # Read Configuration from target Configuration File Path
        self.read_configuration_file()

        # Create the Flask app
        self.app = Flask(__name__, template_folder=template_dir)

        # Add URL rules to the Flask app mapping the URL to the function
        self.app.add_url_rule('/home', 'home', self.info)
        self.app.add_url_rule('/position/flock_center', 'telemetry', self.telemetry)
        self.app.add_url_rule('/position/drones_center', 'telemetry_d', self.telemetry_d)
        self.app.add_url_rule('/environment', 'environment', self.environment)
        self.app.add_url_rule('/controls', 'controls', self.controls)
        self.app.add_url_rule('/controls/button-input-points', 'button-input-points', self.button_control_input, methods=['PUT'])
    
    def controls(self):
        return render_template('controls.html')
    

    def button_control_input(self):
        data = request.json  # Get JSON data from request
        #data = json.loads(json_data)
        if "mission_points" in data and isinstance(data["mission_points"], list):
            
            points = data["mission_points"]
            mission_type = data['mission_type']
            response_message = f"Received mission points: {points}\nMission type: {mission_type}"
            # Get the base URL from the configuration
            base_http_url = self.configuration_dict['web']['api_base_url']
            target_url = f'{base_http_url}/controls/mission-points'
            print(data)
            try:
                # Send the PUT request
                response_string = requests.put(target_url, json=data, timeout=5) # Send the PUT request
                print("response string:", response_string.content.decode())
            except:
                return jsonify({"Error": "in sending data to API server"}), 500
            print("after except")
            return jsonify({"response from api server": response_string.content.decode()}), response_string.status_code
        return jsonify({"error": "Invalid request"}), 400

    def read_configuration_file(self):
        """ Read Configuration File for the Web Server
         :return:
        """

        # Get the main communication directory
        main_app_path = ""

        # Construct the file path
        file_path = os.path.join(main_app_path, self.config_file)

        with open(file_path, 'r') as file:
            self.configuration_dict = yaml.safe_load(file)

        print("Read Configuration from file ({}): {}".format(self.config_file, self.configuration_dict))

    def telemetry(self):
        """ Get telemetry data and render the telemetry.html template"""
        telemetry_data = self.http_get_device_telemetry()
        print(telemetry_data)
        return render_template('flock_center_telemetry.html', telemetry_data=telemetry_data)

    def http_get_device_telemetry(self):
        """ Get all locations from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/position/flock_center'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()


    def telemetry_d(self):
        """ Get telemetry data and render the telemetry.html template"""
        telemetry_data = self.http_get_device_telemetry_d()
        print(telemetry_data)
        return render_template('drone_center_telemetry.html', telemetry_data=telemetry_data)

    def http_get_device_telemetry_d(self):
        """ Get all locations from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/position/drones_center'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()


    def environment(self):
        """ Get telemetry data and render the telemetry.html template"""
        telemetry_data = self.http_get_environment()
        print(telemetry_data)
        return render_template('environment.html', telemetry_data=telemetry_data)

    def http_get_environment(self):
        """ Get all locations from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/environment'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()


    def devices(self, location_id):
        """ Get all devices for a specific location and render the devices.html template"""
        device_list = self.http_get_device_list(location_id)
        return render_template('devices.html', devices=device_list, location_id=location_id)

    def http_get_device_list(self, location_id):
        """ Get all devices for the target location_id from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/location/{location_id}/device'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()


    def run_server(self):
        """ Run the Flask Web Server"""
        self.app.run(host=self.configuration_dict['web']['host'], port=self.configuration_dict['web']['port'])

    def start(self):
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

    def stop(self):
        """ Stop the REST API Server (Flask Method)
        In this code, request.environ.get('werkzeug.server.shutdown')
        retrieves the shutdown function from the environment.
        If the function is not found, it raises a RuntimeError,
        indicating that the server is not running with Werkzeug.
        If the function is found, it is called to shut down the server."""

        # Shutdown the server
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')

        # Call the shutdown function
        func()

        # Wait for the server thread to join
        self.server_thread.join()


    def info(self):
        info_data = self.http_get_device_info()
        return render_template('home.html', info_data=info_data)
    
    def http_get_device_info(self):
        """ Get all locations from the remote server over HTTP"""

        # Get the base URL from the configuration
        base_http_url = self.configuration_dict['web']['api_base_url']
        target_url = f'{base_http_url}/info'

        # Send the GET request
        response_string = requests.get(target_url)

        # Return the JSON response
        return response_string.json()
    