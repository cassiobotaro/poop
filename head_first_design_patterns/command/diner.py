"""
Notes:
    - Command was used here to indicate that the expected type
    is a function with no arguments and no return value
    - Order (line 24) should be a command
    - Customer can create an order (simplified here for just one order)
    - Customer take order using waitress instance
    - Waitress take order without know the order implementation
    - When you order something, cook is called to make your diner
    - Note that the kitchen invokes the preparation of the order without
    knowing how it will be prepared by the cook
"""


from typing import Callable, Optional

Command = Callable[[], None]


class Cook:
    def make_burger(self):
        print("Making a burger")

    def make_fries(self):
        print("Making fries")


class Waitress:
    def __init__(self):
        self.order = None

    def take_order(self, order: Command) -> None:
        self.order = order
        order()


class Customer:
    def __init__(self, waitress: Waitress, cook: Cook):
        self.waitress = waitress
        self.cook = cook
        self.order: Optional[Command] = None

    def create_order(self):
        def burger_and_fries():
            self.cook.make_burger()
            self.cook.make_fries()

        self.order = burger_and_fries

    def hungry(self):
        self.waitress.take_order(self.order)


if __name__ == "__main__":
    cook = Cook()
    waitress = Waitress()
    customer = Customer(waitress, cook)
    customer.create_order()
    customer.hungry()
