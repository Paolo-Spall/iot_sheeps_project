import json

class ServiceMessage:
    def __init__(self, data_type, timestamp, alerts):
        self.data_type = data_type
        self.timestamp = timestamp
        self.alerts = alerts

    def __repr__(self):
        return f"ServiceMessage(data_type={self.data_type}, timestamp={self.timestamp}, alerts={self.alerts})"

    def to_json(self):
        return json.dumps(self.__dict__)
    
    def to_dict(self):
        """Restituisce l'oggetto come un dizionario"""
        return self.__dict__

    def to_readable_string(self):
            """Restituisce una rappresentazione leggibile dell'oggetto."""
            readable_message = f"Data Type: {self.data_type}\n"
            readable_message += f"Timestamp: {self.timestamp}\n"
            if self.alerts:
                readable_message += "Alerts:\n" + "\n".join(f"  - {alert}" for alert in self.alerts)
            else:
                readable_message += "Alerts: None"
            return readable_message
    
