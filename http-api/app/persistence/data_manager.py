class DataManager:
    """
    DataManager class is responsible for managing the data of the application.
    Abstracts the data storage and retrieval operations.
    In this implementation everything is stored in memory.
    """

    # The data structure to store the telemetry data
    data_manager_dict = {}   #Lista di punti di missione
    flock_timeseries_data = []   #Telemetry aggiornata istante per istante
    drones_timeseries_data = []   #Telemetry aggiornata istante per istante
    environmental_data = []
    info_data = {}
    

    def add_device_telemetry_data_by_device_id(self, device_id, telemetry_data):
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

    def add_flock_telemetry_data(self, telemetry_data):
        """Add a new telemetry data for a given device"""
        self.flock_timeseries_data.append(telemetry_data)

    def get_flock_data(self):
        return self.flock_timeseries_data

    def add_drones_telemetry_data(self, telemetry_data):
        """Add a new telemetry data for a given device"""
        self.drones_timeseries_data.append(telemetry_data)

    def get_drones_data(self):
        return self.drones_timeseries_data

    def get_environmental_data(self):
        return self.environmental_data

    def update_environmental_data(self, payload):
        if len(self.environmental_data) == 0:
            self.environmental_data.append(payload)
        else:
            self.environmental_data[0] = payload

    def update_info_data(self, device_id, payload):
        """Add a new telemetry data for a given device"""
        if not isinstance(device_id, str):
            raise ValueError(f"device_id must be a string, got {type(device_id)}: {device_id}")

        if device_id not in self.info_data:
            self.info_data[device_id] = []
        self.info_data[device_id] = payload

    def get_info_data(self, device_id):
        """Return the telemetry data for a given device"""
        return self.info_data
    
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