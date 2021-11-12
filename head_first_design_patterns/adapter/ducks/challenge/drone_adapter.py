from head_first_design_patterns.adapter.ducks.challenge.drone import Drone


class DroneAdapter:
    def __init__(self, drone: Drone) -> None:
        self.drone = drone

    def quack(self) -> None:
        self.drone.beep()

    def fly(self) -> None:
        self.drone.spin_rotors()
        self.drone.take_off()
