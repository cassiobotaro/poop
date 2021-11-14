from typing import Protocol


class Command(Protocol):
    def execute(self) -> None:
        ...

    def undo(self) -> None:
        ...
