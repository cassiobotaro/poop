class Screen:
    def __init__(self, description: str) -> None:
        self._description = description

    def up(self) -> None:
        print(f"{self._description} going up")

    def down(self) -> None:
        print(f"{self._description} going down")

    def __str__(self) -> str:
        return self._description
