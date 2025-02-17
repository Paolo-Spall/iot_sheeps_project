class DataManager:
    """
    DataManager class is responsible for managing the data of the application.
    Abstracts the data storage and retrieval operations.
    In this implementation everything is stored in memory.
    """

    # The data structure to store the telemetry data
    data_manager_dict = {}
    device_timeseries_data = {}

    def add_device_telemetry_data(self, device_id, telemetry_data):
        """Add a new telemetry data for a given device"""
        if device_id not in self.device_timeseries_data:
            self.device_timeseries_data[device_id] = []
        self.device_timeseries_data[device_id].append(telemetry_data)

    def get_telemetry_data_by_device_id(self, device_id):
        """Return the telemetry data for a given device"""
        if device_id in self.device_timeseries_data:
            return self.device_timeseries_data[device_id]
        else:
            return None
    
    def init_mission(self):
        self.data_manager_dict['mission'] = {}

    def get_mission(self):
        return self.data_manager_dict['mission']

    def update_mission(self, mission_type, mission_points):
        """Update the mission points for the drone"""
        if "mission" not in self.data_manager_dict:
            self.data_manager_dict["mission"] = {}
        self.data_manager_dict["mission"]["mission_type"] = mission_type
        self.data_manager_dict["mission"]["mission_points"] = mission_points