from poop.hfdp.factory.pizzaaf.black_olives import BlackOlives
from poop.hfdp.factory.pizzaaf.cheese import Cheese
from poop.hfdp.factory.pizzaaf.clams import Clams
from poop.hfdp.factory.pizzaaf.dough import Dough
from poop.hfdp.factory.pizzaaf.eggplant import Eggplant
from poop.hfdp.factory.pizzaaf.frozen_clams import FrozenClams
from poop.hfdp.factory.pizzaaf.mozzarella_cheese import MozzarellaCheese
from poop.hfdp.factory.pizzaaf.pepperoni import Pepperoni
from poop.hfdp.factory.pizzaaf.pizza_ingredient_factory import (
    PizzaIngredientFactory,
)
from poop.hfdp.factory.pizzaaf.plum_tomato_sauce import PlumTomatoSauce
from poop.hfdp.factory.pizzaaf.sauce import Sauce
from poop.hfdp.factory.pizzaaf.sliced_pepperoni import SlicedPepperoni
from poop.hfdp.factory.pizzaaf.spinach import Spinach
from poop.hfdp.factory.pizzaaf.thick_crust_dough import ThickCrustDough
from poop.hfdp.factory.pizzaaf.veggies import Veggies


class ChicagoPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:
        return ThickCrustDough()

    def create_sauce(self) -> Sauce:
        return PlumTomatoSauce()

    def create_cheese(self) -> Cheese:
        return MozzarellaCheese()

    def create_veggies(self) -> list[Veggies]:
        return [BlackOlives(), Spinach(), Eggplant()]

    def create_pepperoni(self) -> Pepperoni:
        return SlicedPepperoni()

    def create_clam(self) -> Clams:
        return FrozenClams()
