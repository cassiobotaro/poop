from poop.hfdp.factory.pizzaaf.chicago_pizza_store import ChicagoPizzaStore
from poop.hfdp.factory.pizzaaf.ny_pizza_store import NYPizzaStore
from poop.hfdp.factory.pizzaaf.pizza import Pizza
from poop.hfdp.factory.pizzaaf.pizza_store import PizzaStore


def main() -> None:
    ny_store: PizzaStore = NYPizzaStore()
    chicago_store: PizzaStore = ChicagoPizzaStore()

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
