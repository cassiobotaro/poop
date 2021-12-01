class PopcornPopper:
    def __init__(self, description: str) -> None:
        self.description = description

    def on(self) -> None:
        print(f"{self.description} on")

    def off(self) -> None:
        print(f"{self.description} off")

    def pop(self) -> None:
        print(f"{self.description} popping popcorn!")

    def __str__(self) -> str:
        return self.description
