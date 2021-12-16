from poop.hfdp.factory.pizzaaf.cheese_pizza import CheesePizza
from poop.hfdp.factory.pizzaaf.clam_pizza import ClamPizza
from poop.hfdp.factory.pizzaaf.ny_pizza_ingredient_factory import (
    NYPizzaIngredientFactory,
)
from poop.hfdp.factory.pizzaaf.pepperoni_pizza import PepperoniPizza
from poop.hfdp.factory.pizzaaf.pizza import Pizza
from poop.hfdp.factory.pizzaaf.pizza_ingredient_factory import (
    PizzaIngredientFactory,
)
from poop.hfdp.factory.pizzaaf.pizza_store import PizzaStore
from poop.hfdp.factory.pizzaaf.veggie_pizza import VeggiePizza


class NYPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza | None:
        ingredient_factory: PizzaIngredientFactory = NYPizzaIngredientFactory()
        pizza: Pizza | None = None
        if flavor == "cheese":
            pizza = CheesePizza(ingredient_factory)
            pizza.set_name("New York Style Cheese Pizza")
        elif flavor == "veggie":
            pizza = VeggiePizza(ingredient_factory)
            pizza.set_name("New York Style Veggie Pizza")
        elif flavor == "clam":
            pizza = ClamPizza(ingredient_factory)
            pizza.set_name("New York Style Clam Pizza")
        elif flavor == "pepperoni":
            pizza = PepperoniPizza(ingredient_factory)
            pizza.set_name("New York Style Pepperoni Pizza")
        return pizza
