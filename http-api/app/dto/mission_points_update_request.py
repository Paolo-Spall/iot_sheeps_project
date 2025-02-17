import json


class MissionPointsUpdateRequest:

    def __init__(self, mission_type, mission_points):
        self.mission_type = mission_type
        self.mission_points = mission_points

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)