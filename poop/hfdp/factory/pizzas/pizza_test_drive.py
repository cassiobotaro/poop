from poop.hfdp.factory.pizzas.pizza_store import PizzaStore
from poop.hfdp.factory.pizzas.simple_pizza_factory import SimplePizzaFactory


def main() -> None:
    factory = SimplePizzaFactory()
    store = PizzaStore(factory)

    pizza = store.order_pizza("cheese")
    print(f"We ordered a  {pizza.get_name()}")
    print(pizza)

    pizza = store.order_pizza("veggie")
    print(f"We ordered a  {pizza.get_name()}")
    print(pizza)
