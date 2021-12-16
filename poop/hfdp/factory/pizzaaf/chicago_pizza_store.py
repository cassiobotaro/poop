from poop.hfdp.factory.pizzaaf.cheese_pizza import CheesePizza
from poop.hfdp.factory.pizzaaf.chicago_pizza_ingredient_factory import (
    ChicagoPizzaIngredientFactory,
)
from poop.hfdp.factory.pizzaaf.clam_pizza import ClamPizza
from poop.hfdp.factory.pizzaaf.pepperoni_pizza import PepperoniPizza
from poop.hfdp.factory.pizzaaf.pizza import Pizza
from poop.hfdp.factory.pizzaaf.pizza_ingredient_factory import (
    PizzaIngredientFactory,
)
from poop.hfdp.factory.pizzaaf.pizza_store import PizzaStore
from poop.hfdp.factory.pizzaaf.veggie_pizza import VeggiePizza


class ChicagoPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza | None:
        ingredient_factory: PizzaIngredientFactory = (
            ChicagoPizzaIngredientFactory()
        )
        pizza: Pizza | None = None
        if flavor == "cheese":
            pizza = CheesePizza(ingredient_factory)
            pizza.set_name("Chicago Style Cheese Pizza")
        elif flavor == "veggie":
            pizza = VeggiePizza(ingredient_factory)
            pizza.set_name("Chicago Style Veggie Pizza")
        elif flavor == "clam":
            pizza = ClamPizza(ingredient_factory)
            pizza.set_name("Chicago Style Clam Pizza")
        elif flavor == "pepperoni":
            pizza = PepperoniPizza(ingredient_factory)
            pizza.set_name("Chicago Style Pepperoni Pizza")
        return pizza
