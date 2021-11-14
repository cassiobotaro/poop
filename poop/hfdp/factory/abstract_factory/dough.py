"""
Notes:
    - Each dough has its own str representation
    - Each ingredient is a product that is produced
    by a Factory Method (create_dough)
    in the Abstract Factory (PizzaIngredientFactory)
    See pizza_ingredient_factory.py
"""
from abc import ABC, abstractmethod


class Dough(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class ThinCrustDough(Dough):
    def __str__(self) -> str:
        return "Thin Crust Dough"


class ThickCrustDough(Dough):
    def __str__(self) -> str:
        return "ThickCrust style extra thick crust dough"
