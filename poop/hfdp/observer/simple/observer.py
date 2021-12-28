from typing import Protocol


class Observer(Protocol):
    def update(self, value: int) -> None:
        ...
