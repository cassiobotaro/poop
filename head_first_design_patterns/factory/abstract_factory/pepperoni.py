"""
Notes:
    - Each pepperoni has its own str representation
    - Each ingredient is a product that is produced
    by a Factory Method (create_pepperoni)
    in the Abstract Factory (PizzaIngredientFactory)
    See pizza_ingredient_factory.py
"""
from abc import ABC, abstractmethod


class Pepperoni(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class SlicedPepperoni(Pepperoni):
    def __str__(self) -> str:
        return "Sliced Pepperoni"
