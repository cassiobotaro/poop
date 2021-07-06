"""
Notes:
    - Pizza is an abstraction, ingredients are optional and are setted
    on prepare method
    - Each concrete pizza defines a name and its ingredients in the
    preparation
    - The "prepare" method uses the factory (which is abstract)
    to add the ingredients through methods that work as factories
    (factory methods) for generating products (ingredients)
    - The factory's product is pizza, and this factory abstracts
    the creation of ingredients (products)
    - Factory is about abstraction of product creation
    - UnknownPizza is a way to avoid some conditionals
"""
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Optional

from cheese import Cheese
from clams import Clams
from dough import Dough
from pepperoni import Pepperoni
from pizza_ingredient_factory import PizzaIngredientFactory
from sauce import Sauce
from veggies import Veggies


class Pizza(ABC):
    @abstractmethod
    def __init__(self):
        self.name: str = ""

        self.dough: Optional[Dough] = None
        self.sauce: Optional[Sauce] = None
        self.veggies: Iterable[Veggies] = []
        self.cheese: Optional[Cheese] = None
        self.pepperoni: Optional[Pepperoni] = None
        self.clams: Optional[Clams] = None

    @abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError

    def bake(self) -> None:
        print("Bake for 25 minutes at 350")

    def cut(self) -> None:
        print("Cut the pizza into diagonal slices")

    def box(self) -> None:
        print("Place pizza in official PizzaStore box")

    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        dough = f"{self.dough}\n" if self.dough else ""
        sauce = f"{self.sauce}\n" if self.sauce else ""
        cheese = f"{self.cheese}\n" if self.cheese else ""
        veggies = (
            ",".join(str(veggie) for veggie in self.veggies) + "\n"
            if self.veggies
            else ""
        )
        clam = f"{self.clams}\n" if self.clams else ""
        pepperoni = f"{self.pepperoni}\n" if self.pepperoni else ""
        return (
            f"---- {self.name} ----\n"
            f"{dough}"
            f"{sauce}"
            f"{cheese}"
            f"{veggies}"
            f"{clam}"
            f"{pepperoni}"
        )


class UnknownPizza(Pizza):
    def __init__(self):
        super().__init__()
        self.name = "unknown flavor"

    def prepare(self) -> None:
        print("Unknown flavor cannot be prepared")


class CheesePizza(Pizza):
    def __init__(self, ingredient_factory: PizzaIngredientFactory):
        super().__init__()
        self.ingredient_factory = ingredient_factory

    def prepare(self) -> None:
        print(f"Preparing {self.name}")
        self.dough = self.ingredient_factory.create_dough()
        self.sauce = self.ingredient_factory.create_sauce()
        self.cheese = self.ingredient_factory.create_cheese()


class ClamPizza(Pizza):
    def __init__(self, ingredient_factory: PizzaIngredientFactory):
        super().__init__()
        self.ingredient_factory = ingredient_factory

    def prepare(self) -> None:
        print(f"Preparing {self.name}")
        self.dough = self.ingredient_factory.create_dough()
        self.sauce = self.ingredient_factory.create_sauce()
        self.cheese = self.ingredient_factory.create_cheese()
        self.clam = self.ingredient_factory.create_clam()


class VeggiePizza(Pizza):
    def __init__(self, ingredient_factory: PizzaIngredientFactory):
        super().__init__()
        self.ingredient_factory = ingredient_factory

    def prepare(self) -> None:
        print(f"Preparing {self.name}")
        self.dough = self.ingredient_factory.create_dough()
        self.sauce = self.ingredient_factory.create_sauce()
        self.cheese = self.ingredient_factory.create_cheese()
        self.veggies = self.ingredient_factory.create_veggies()


class PepperoniPizza(Pizza):
    def __init__(self, ingredient_factory: PizzaIngredientFactory):
        super().__init__()
        self.ingredient_factory = ingredient_factory

    def prepare(self) -> None:
        print(f"Preparing {self.name}")
        self.dough = self.ingredient_factory.create_dough()
        self.sauce = self.ingredient_factory.create_sauce()
        self.cheese = self.ingredient_factory.create_cheese()
        self.veggies = self.ingredient_factory.create_veggies()
        self.pepperoni = self.ingredient_factory.create_pepperoni()
