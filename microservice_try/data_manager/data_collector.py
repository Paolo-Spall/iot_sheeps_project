
class DataCollector:
    last_device_data = {}

    def add_last_device_data(self, device_id, telemetry_data):
        if device_id not in self.last_device_data:
            self.last_device_data[device_id] = []
        self.last_device_data[device_id] = telemetry_data

    def get_last_device_data(self):
        return list(self.last_device_data.values())

    def delete_last_device_data(self):
        self.last_device_data = {}