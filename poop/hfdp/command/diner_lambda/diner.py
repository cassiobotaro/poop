from poop.hfdp.command.diner_lambda.cook import Cook
from poop.hfdp.command.diner_lambda.customer import Customer
from poop.hfdp.command.diner_lambda.waitress import Waitress


def main() -> None:
    cook = Cook()
    waitress = Waitress()
    customer = Customer(waitress, cook)
    customer.create_order()
    customer.hungry()
