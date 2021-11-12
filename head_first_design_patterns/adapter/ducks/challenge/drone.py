from typing import Protocol


class Drone(Protocol):
    def beep(self) -> None:
        ...

    def spin_rotors(self) -> None:
        ...

    def take_off(self) -> None:
        ...
