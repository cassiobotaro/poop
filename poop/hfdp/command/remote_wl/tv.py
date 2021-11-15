from typing import Final


class TV:
    INITIAL_CHANNEL: Final[int] = 0
    DVD_CHANNEL: Final[int] = 3

    def __init__(self, location: str) -> None:
        self.__location = location
        self.__channel = self.INITIAL_CHANNEL

    def on(self) -> None:
        print(f"{self.__location} TV is on")

    def off(self) -> None:
        print(f"{self.__location} TV is off")

    def set_input_channel(self) -> None:
        self.__channel = self.DVD_CHANNEL
        print(f"{self.__location} TV is set for DVD")
