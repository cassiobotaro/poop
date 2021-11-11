"""Notes
- Drone is a protocol that defines the interface for a drone.
- SuperDrone is a concrete implementation of the Drone protocol.
- Don't need inheritance because of structural typing.
- DroneAdapter is a concrete implementation of the Duck protocol.
- Even it sounds confuse, we are adapting a Drone to beheave like a Duck.
"""
from typing import Protocol


class Drone(Protocol):
    def beep(self) -> None:
        ...

    def spin_rotors(self) -> None:
        ...

    def take_off(self) -> None:
        ...


class DroneAdapter:
    def __init__(self, drone: Drone) -> None:
        self.drone = drone

    def quack(self) -> None:
        self.drone.beep()

    def fly(self) -> None:
        self.drone.spin_rotors()
        self.drone.take_off()


class SuperDrone:
    def beep(self) -> None:
        print("Beep beep beep")

    def spin_rotors(self) -> None:
        print("Rotors are spinning")

    def take_off(self) -> None:
        print("Taking off")
