from poop.hfdp.factory.pizzas.cheese_pizza import CheesePizza
from poop.hfdp.factory.pizzas.clam_pizza import ClamPizza
from poop.hfdp.factory.pizzas.pepperoni_pizza import PepperoniPizza
from poop.hfdp.factory.pizzas.pizza import Pizza
from poop.hfdp.factory.pizzas.veggie_pizza import VeggiePizza


class SimplePizzaFactory:
    def create_pizza(self, flavor: str) -> Pizza | None:
        if flavor == "cheese":
            return CheesePizza()
        elif flavor == "clam":
            return ClamPizza()
        elif flavor == "veggie":
            return VeggiePizza()
        elif flavor == "pepperoni":
            return PepperoniPizza()
        return None
