from abc import ABC, abstractmethod

from poop.hfdp.factory.pizzaaf.cheese import Cheese
from poop.hfdp.factory.pizzaaf.clams import Clams
from poop.hfdp.factory.pizzaaf.dough import Dough
from poop.hfdp.factory.pizzaaf.pepperoni import Pepperoni
from poop.hfdp.factory.pizzaaf.sauce import Sauce
from poop.hfdp.factory.pizzaaf.veggies import Veggies


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
