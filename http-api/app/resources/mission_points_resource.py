from json import JSONDecodeError
from flask import request, Response
from flask_restful import Resource
import requests
from dto.location_update_request import LocationUpdateRequest

class MissionPoints(Resource):
    """Resource to handle the Telemetry Data of a specific Device"""

    def __init__(self, **kwargs):
        
        # Inject the DataManager instance
        self.data_manager = kwargs['data_manager']
        self.gateaway_url = kwargs['gateaway_url']


    def put(self):
        try:

            json_data = request.get_json(force=True)
            location_update_request = LocationUpdateRequest(**json_data)
            mission_type = location_update_request.mission_type
            mission_points = location_update_request.points

        except Exception as e:
            return {'error': "Data format error ! Reason: " + str(e)}, 400
        
        self.data_manager.update_mission(mission_type, mission_points)
        # Send the PUT request
        response = requests.put(self.gateaway_url, json=location_update_request.to_json())
        
        
        return response.content,response.status_code
    

