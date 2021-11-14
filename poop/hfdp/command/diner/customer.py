from typing import Optional

from poop.hfdp.command.diner.order import Order
from poop.hfdp.command.diner.waitress import Waitress


class Customer:
    def __init__(self, waitress: Waitress) -> None:
        self.waitress = waitress
        self.order: Optional[Order] = None

    def create_order(self, order: Order) -> None:
        self.order = order

    def hungry(self) -> None:
        if self.order is not None:
            self.waitress.take_order(self.order)
