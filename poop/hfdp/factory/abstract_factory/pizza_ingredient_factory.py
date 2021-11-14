"""
Notes:
    - abstract factory interface declares a set of methods for
      creating each of the abstract products.
    - each concrete class defines its own products (ingredients)
    - the returns are abstractions of the ingredients (abstract types)
"""
from abc import ABC, abstractmethod

from cheese import Cheese, MozzarellaCheese, ReggianoCheese
from clams import Clams, FreshClams, FrozenClams
from dough import Dough, ThickCrustDough, ThinCrustDough
from pepperoni import Pepperoni, SlicedPepperoni
from sauce import MarinaraSauce, PlumTomatoSauce, Sauce
from veggies import (
    BlackOlives,
    Eggplant,
    Garlic,
    Mushroom,
    Onion,
    RedPepper,
    Spinach,
    Veggies,
)


class PizzaIngredientFactory(ABC):
    @abstractmethod
    def create_dough(self) -> Dough:
        raise NotImplementedError

    @abstractmethod
    def create_sauce(self) -> Sauce:
        raise NotImplementedError

    @abstractmethod
    def create_cheese(self) -> Cheese:
        raise NotImplementedError

    @abstractmethod
    def create_veggies(self) -> list[Veggies]:
        raise NotImplementedError

    @abstractmethod
    def create_pepperoni(self) -> Pepperoni:
        raise NotImplementedError

    @abstractmethod
    def create_clam(self) -> Clams:
        raise NotImplementedError


class NYPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:
        return ThinCrustDough()

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
