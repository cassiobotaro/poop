"""
Notes:
    - Each sauce has its own str representation
    - Each ingredient is a product that is produced
    by a Factory Method (create_sauce)
    in the Abstract Factory (PizzaIngredientFactory)
    See pizza_ingredient_factory.py
"""
from abc import ABC, abstractmethod


class Sauce(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class MarinaraSauce(Sauce):
    def __str__(self) -> str:
        return "Marinara Sauce"


class PlumTomatoSauce(Sauce):
    def __str__(self) -> str:
        return "Tomato sauce with plum tomatoes"
