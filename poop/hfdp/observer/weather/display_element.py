from typing import Protocol


class DisplayElement(Protocol):
    def display(self) -> None:
        ...
