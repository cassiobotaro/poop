from poop.hfdp.command.diner.order import Order


class Waitress:
    def __init__(self) -> None:
        self.order: Order | None = None

    def take_order(self, order: Order) -> None:
        self.order = order
        self.order.order_up()
