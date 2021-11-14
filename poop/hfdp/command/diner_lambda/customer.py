from typing import Optional

from poop.hfdp.command.diner_lambda.cook import Cook
from poop.hfdp.command.diner_lambda.order import Order
from poop.hfdp.command.diner_lambda.waitress import Waitress


class Customer:
    def __init__(self, waitress: Waitress, cook: Cook) -> None:
        self.waitress = waitress
        self.cook = cook
        self.order: Optional[Order] = None

    def create_order(self) -> None:
        def order_burger_and_fries() -> None:
            self.cook.make_burger()
            self.cook.make_fries()

        self.order = order_burger_and_fries

    def hungry(self) -> None:
        if self.order is not None:
            self.waitress.take_order(self.order)
