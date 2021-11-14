from poop.hfdp.command.diner.burger_and_fries_order import BurgerAndFriesOrder
from poop.hfdp.command.diner.cook import Cook
from poop.hfdp.command.diner.customer import Customer
from poop.hfdp.command.diner.waitress import Waitress


def main() -> None:
    cook = Cook()
    waitress = Waitress()
    customer = Customer(waitress)
    customer.create_order(BurgerAndFriesOrder(cook))
    customer.hungry()
