from json import JSONDecodeError
import json
from flask import request, Response
from flask_restful import Resource

class DronesInfo(Resource):
    """Resource to handle the Telemetry Data of a specific Device"""

    def __init__(self, **kwargs):
        # Inject the DataManager instance
        self.data_manager = kwargs['data_manager']

    def get(self):
        return self.data_manager.get_info(), 200