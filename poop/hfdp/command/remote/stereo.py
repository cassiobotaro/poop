class Stereo:
    def __init__(self, location: str) -> None:
        self.__location = location

    def on(self) -> None:
        print(f"{self.__location} stereo is on")

    def off(self) -> None:
        print(f"{self.__location} stereo is off")

    def set_cd(self) -> None:
        print(f"{self.__location} is set for CD input")

    def set_dvd(self) -> None:
        print(f"{self.__location} is set for DVD input")

    def set_radio(self) -> None:
        print(f"{self.__location} is set for Radio")

    def set_volume(self, volume: int) -> None:
        print(f"{self.__location} Stereo volume set to {volume}")
