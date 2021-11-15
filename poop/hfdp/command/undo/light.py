from typing import Final


class Light:
    OFF_LEVEL: Final[int] = 0
    ON_LEVEL: Final[int] = 100

    def __init__(self, location: str) -> None:
        self.__level = self.OFF_LEVEL
        self.__location = location

    def on(self) -> None:
        self.__level = self.ON_LEVEL
        print(f"{self.__location} light is on")

    def off(self) -> None:
        self.__level = self.OFF_LEVEL
        print(f"{self.__location} light is off")

    def dim(self, level: int) -> None:
        self.__level = level
        if level == self.OFF_LEVEL:
            self.off()
        else:
            print(f"Light is dimmed to {self.__level}%")

    def get_level(self) -> int:
        return self.__level
