from json import JSONDecodeError
from flask import request, Response
from flask_restful import Resource
import requests
from dto.mission_points_update_request import MissionPointsUpdateRequest
import json

class MissionPoints(Resource):
    """Resource to handle the Telemetry Data of a specific Device"""

    def __init__(self, **kwargs):
        
        # Inject the DataManager instance
        self.data_manager = kwargs['data_manager']
        self.gateway_url = kwargs['control_input_url']
        self.data_manager.init_mission()


    def put(self):
        try:

            json_data = request.get_json(force=True)
            location_update_request = MissionPointsUpdateRequest(**json_data)
            mission_type = location_update_request.mission_type
            mission_points = location_update_request.mission_points

        except:
            return json.dumps({'error': "Data format error ! Reason: "}), 400
        try:
            print('before saving mission')
            self.data_manager.update_mission(mission_type, mission_points)
            print('after saving mission')
        except:
            return json.dumps({'error': "Error in storing data ! Reason: "}), 500
        
        # Send the PUT request
        response = requests.put(self.gateway_url, json=location_update_request.to_json())
        
        return json.dumps({'gateway_response': response.content.decode()}),response.status_code
    
    def get(self):
        mission = self.data_manager.get_mission()
        return mission, 200

