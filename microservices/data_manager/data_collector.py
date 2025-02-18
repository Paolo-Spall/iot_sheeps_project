
class DataCollector:
    last_device_data = {}
    point_list = []

    def add_last_device_data(self, device_id, telemetry_data):
        if device_id not in self.last_device_data:
            self.last_device_data[device_id] = []
        self.last_device_data[device_id] = telemetry_data

    def get_last_device_data(self):
        return list(self.last_device_data.values())

    def delete_last_device_data(self):
        self.last_device_data = {}

    def add_points_list(self, points):
        self.point_list = points

    def remove_point(self):
        if isinstance(self.point_list, dict) and "mission_points" in self.point_list:
            if self.point_list["mission_points"]:
                self.point_list["mission_points"].pop(0)
            else:
                print("La lista mission_points è vuota.")
        else:
            print("La struttura di point_list non è quella prevista.")

    def get_points_list(self):
        return self.point_list