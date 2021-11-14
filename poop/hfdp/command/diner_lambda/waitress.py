from typing import Optional

from poop.hfdp.command.diner_lambda.order import Order


class Waitress:
    def __init__(self) -> None:
        self.order: Optional[Order] = None

    def take_order(self, order: Order) -> None:
        self.order = order
        self.order()
