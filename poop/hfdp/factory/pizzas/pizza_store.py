from poop.hfdp.factory.pizzas.pizza import Pizza
from poop.hfdp.factory.pizzas.simple_pizza_factory import SimplePizzaFactory


class PizzaStore:
    def __init__(self, factory: SimplePizzaFactory):
        self.factory = factory

    def order_pizza(self, flavor: str) -> Pizza:
        pizza = self.factory.create_pizza(flavor)
        if pizza is None:
            raise ValueError(f"Invalid pizza flavor: {flavor}")
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza
