from poop.hfdp.factory.pizzafm.ny_style_cheese_pizza import NYStyleCheesePizza
from poop.hfdp.factory.pizzafm.ny_style_clam_pizza import NYStyleClamPizza
from poop.hfdp.factory.pizzafm.ny_style_pepperoni_pizza import (
    NYStylePepperoniPizza,
)
from poop.hfdp.factory.pizzafm.ny_style_veggie_pizza import NYStyleVeggiePizza
from poop.hfdp.factory.pizzafm.pizza import Pizza
from poop.hfdp.factory.pizzafm.pizza_store import PizzaStore


class NYPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza | None:
        if flavor == "cheese":
            return NYStyleCheesePizza()
        elif flavor == "veggie":
            return NYStyleVeggiePizza()
        elif flavor == "clam":
            return NYStyleClamPizza()
        elif flavor == "pepperoni":
            return NYStylePepperoniPizza()
        return None
