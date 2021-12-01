class TheaterLights:
    def __init__(self, description: str) -> None:
        self._description = description

    def on(self) -> None:
        print(f"{self._description} on")

    def off(self) -> None:
        print(f"{self._description} off")

    def dim(self, level: int) -> None:
        print(f"{self._description} dimming to {level}%")

    def __str__(self) -> str:
        return self._description
