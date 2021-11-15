class GarageDoor:
    def __init__(self, location: str) -> None:
        self.__location = location

    def up(self) -> None:
        print(f"{self.__location} garage door is up")

    def down(self) -> None:
        print(f"{self.__location} garage door is down")

    def stop(self) -> None:
        print(f"{self.__location} garage door is stopped")

    def light_on(self) -> None:
        print(f"{self.__location} garage light is on")

    def light_off(self) -> None:
        print(f"{self.__location} garage light is off")
