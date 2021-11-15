from enum import Enum

SPEED = Enum("SPEED", "HIGH MEDIUM LOW OFF")


class CeilingFan:
    def __init__(self, location: str) -> None:
        self.__location = location
        self.__speed: SPEED = SPEED.OFF

    def high(self) -> None:
        self.__speed = SPEED.HIGH
        print(f"{self.__location} ceiling fan is on high")

    def medium(self) -> None:
        self.__speed = SPEED.MEDIUM
        print(f"{self.__location} ceiling fan is on medium")

    def low(self) -> None:
        self.__speed = SPEED.LOW
        print(f"{self.__location} ceiling fan is on low")

    def off(self) -> None:
        self.__speed = SPEED.OFF
        print(f"{self.__location} ceiling fan is off")

    def get_speed(self) -> SPEED:
        return self.__speed
