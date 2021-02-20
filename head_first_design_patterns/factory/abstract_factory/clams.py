"""
Notes:
    - Each clam has its own str representation
    - Each ingredient is a product that is produced
    by a Factory Method (create_clam)
    in the Abstract Factory (PizzaIngredientFactory)
    See pizza_ingredient_factory.py
"""
from abc import ABC, abstractmethod


class Clams(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class FrozenClams(Clams):
    def __str__(self) -> str:
        return "Frozen Clams from Chesapeake Bay"


class FreshClams(Clams):
    def __str__(self) -> str:
        return "Fresh Clams from Long Island Sound"
