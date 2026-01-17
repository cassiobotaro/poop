from typing import Protocol


class Observer(Protocol):
    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None: ...
