from poop.hfdp.adapter.ducks.challenge.drone import Drone


class DroneAdapter:
    def __init__(self, drone: Drone) -> None:
        self.__drone = drone

    def quack(self) -> None:
        self.__drone.beep()

    def fly(self) -> None:
        self.__drone.spin_rotors()
        self.__drone.take_off()
