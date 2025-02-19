from json import JSONDecodeError
import json
from flask import request, Response
from flask_restful import Resource

class DroneInfo(Resource):
    """Resource to handle the Telemetry Data of a specific Device"""

    def __init__(self, **kwargs):
        # Inject the DataManager instance
        self.data_manager = kwargs['data_manager']

    def get(self, device_id):
        if device_id in self.data_manager.info_data:
            return self.data_manager.get_info_data(device_id), 200
        else:
            return {'error': "Device Not Found !"}, 404

    def put(self, device_id):
        try:

            # The boolean flag force the parsing of POST data as JSON irrespective of the mimetype
            telemetry_data_dict = request.get_json(force=True)
            #telemetry_data_dict = json.loads(telemetry_payload)
            # Deserialize the payload into a TelemetryMessge object
            #telemetry_message = TelemetryMessage(**telemetry_json_data)

            # Add the telemetry data to the data manager
            self.data_manager.update_info_data(device_id, telemetry_data_dict)

            return Response(status=201)  # return 201 Created

        except JSONDecodeError:
            return {'error': "Invalid JSON ! Check the request"}, 400
        except Exception as e:
            return {'error': "Generic Internal Server Error ! Reason: " + str(e)}, 500


