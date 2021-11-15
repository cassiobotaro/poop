from typing import Final


class Hottub:
    INITIAL_TEMP: Final[int] = 0

    def __init__(self) -> None:
        self.__temperature = self.INITIAL_TEMP
        self.__on = False

    def on(self) -> None:
        self.__on = True

    def off(self) -> None:
        self.__on = False

    def bubbles_on(self) -> None:
        if self.__on:
            print("Hottub is bubbling")

    def bubbles_off(self) -> None:
        if self.__on:
            print("Hottub is not bubbling")

    def jets_on(self) -> None:
        if self.__on:
            print("Hottub jets are on")

    def jets_off(self) -> None:
        if self.__on:
            print("Hottub jets are off")

    def set_temperature(self, temperature: int) -> None:
        self.__temperature = temperature

    def heat(self) -> None:
        self.__temperature = 105
        print("Hottub is heating to a steaming 105 degrees")

    def cool(self) -> None:
        self.__temperature = 98
        print("Hottub is cooling to 98 degrees")
