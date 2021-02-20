"""
Notes:
    - use composition to decouple logic to create a pizza
    - order_pizza trusts that the factory will return a
    type of pizza (abstraction of this example)
    - still depends on concrete SimplePizzaFactory, but moves the logic
"""
from pizza import Pizza
from pizza_factory import SimplePizzaFactory


class PizzaStore:
    def __init__(self, factory: SimplePizzaFactory):
        self.factory = factory

    def order_pizza(self, flavor: str) -> Pizza:
        pizza = self.factory.create_pizza(flavor)
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza
