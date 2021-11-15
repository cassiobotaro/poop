class Light:
    def __init__(self, location: str) -> None:
        self.__location = location

    def on(self) -> None:
        print(f"{self.__location} light is on")

    def off(self) -> None:
        print(f"{self.__location} light is off")
