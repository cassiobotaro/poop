from typing import Protocol


class Duck(Protocol):
    def quack(self) -> None:
        ...

    def fly(self) -> None:
        ...
