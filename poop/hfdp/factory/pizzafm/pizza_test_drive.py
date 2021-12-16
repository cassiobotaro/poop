from poop.hfdp.factory.pizzafm.chicago_pizza_store import ChicagoPizzaStore
from poop.hfdp.factory.pizzafm.ny_pizza_store import NYPizzaStore
from poop.hfdp.factory.pizzafm.pizza import Pizza


def main() -> None:
    ny_store: NYPizzaStore = NYPizzaStore()
    chicago_store: ChicagoPizzaStore = ChicagoPizzaStore()

    pizza: Pizza = ny_store.order_pizza("cheese")
    print(f"Ethan ordered a {pizza.get_name()}")

    pizza = chicago_store.order_pizza("cheese")
    print(f"Joel ordered a {pizza.get_name()}")

    pizza = ny_store.order_pizza("clam")
    print(f"Ethan ordered a {pizza.get_name()}")

    pizza = chicago_store.order_pizza("clam")
    print(f"Joel ordered a {pizza.get_name()}")

    pizza = ny_store.order_pizza("pepperoni")
    print(f"Ethan ordered a {pizza.get_name()}")

    pizza = chicago_store.order_pizza("pepperoni")
    print(f"Joel ordered a {pizza.get_name()}")

    pizza = ny_store.order_pizza("veggie")
    print(f"Ethan ordered a {pizza.get_name()}")

    pizza = chicago_store.order_pizza("veggie")
    print(f"Joel ordered a {pizza.get_name()}")
