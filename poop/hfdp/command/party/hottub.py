from typing import Final


class Hottub:
    INITIAL_TEMP: Final[int] = 0

    def __init__(self) -> None:
        self.__temperature = self.INITIAL_TEMP
        self.__on = False

    def on(self) -> None:
        self.__on = True

    def off(self) -> None:
        self.__off = False

    def circulate(self) -> None:
        if self.__on:
            print("Hottub is bubbling")

    def jets_on(self) -> None:
        if self.__on:
            print("Hottub jets are on")

    def jets_off(self) -> None:
        if self.__on:
            print("Hottub jets are off")

    def set_temperature(self, temperature: int) -> None:
        if temperature > self.__temperature:
            print(f"Hottub is heating to a steaming {temperature} degrees")
        else:
            print(f"Hottub is cooling to {temperature} degrees")
        self.__temperature = temperature
