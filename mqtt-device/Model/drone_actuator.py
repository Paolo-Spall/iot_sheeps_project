
class Drone_actuator:
    dt = 0.1

    def __init__(self,P):
        self.position = P
        self.velocity = 0

    # Another instance method with a parameter
    def control_input(self,control_input):
        self.velocity = control_input
        self.position = self.position + self.dt*self.velocity
