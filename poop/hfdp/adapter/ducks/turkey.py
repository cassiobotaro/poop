from typing import Protocol


class Turkey(Protocol):
    def gobble(self) -> None:
        ...

    def fly(self) -> None:
        ...
