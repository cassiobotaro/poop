from poop.hfdp.factory.pizzaaf.cheese import Cheese
from poop.hfdp.factory.pizzaaf.clams import Clams
from poop.hfdp.factory.pizzaaf.dough import Dough
from poop.hfdp.factory.pizzaaf.fresh_clams import FreshClams
from poop.hfdp.factory.pizzaaf.garlic import Garlic
from poop.hfdp.factory.pizzaaf.marinara_sauce import MarinaraSauce
from poop.hfdp.factory.pizzaaf.mushroom import Mushroom
from poop.hfdp.factory.pizzaaf.onion import Onion
from poop.hfdp.factory.pizzaaf.pepperoni import Pepperoni
from poop.hfdp.factory.pizzaaf.pizza_ingredient_factory import (
    PizzaIngredientFactory,
)
from poop.hfdp.factory.pizzaaf.red_pepper import RedPepper
from poop.hfdp.factory.pizzaaf.reggiano_pizza import ReggianoCheese
from poop.hfdp.factory.pizzaaf.sauce import Sauce
from poop.hfdp.factory.pizzaaf.sliced_pepperoni import SlicedPepperoni
from poop.hfdp.factory.pizzaaf.thick_crust_dough import ThickCrustDough
from poop.hfdp.factory.pizzaaf.veggies import Veggies


class NYPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:
        return ThickCrustDough()

    def create_sauce(self) -> Sauce:
        return MarinaraSauce()

    def create_cheese(self) -> Cheese:
        return ReggianoCheese()

    def create_veggies(self) -> list[Veggies]:
        return [Garlic(), Onion(), Mushroom(), RedPepper()]

    def create_pepperoni(self) -> Pepperoni:
        return SlicedPepperoni()

    def create_clam(self) -> Clams:
        return FreshClams()
