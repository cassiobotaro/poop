from typing import Protocol


class Order(Protocol):
    def order_up(self) -> None: ...
