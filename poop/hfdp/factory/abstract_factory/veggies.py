"""
Notes:
    - Each veggie has its own str representation
    - Each ingredient is a product that is produced
    by a Factory Method (create_veggie)
    in the Abstract Factory (PizzaIngredientFactory)
    See pizza_ingredient_factory.py
"""
from abc import ABC, abstractmethod


class Veggies(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class Onion(Veggies):
    def __str__(self) -> str:
        return "Onion"


class Garlic(Veggies):
    def __str__(self) -> str:
        return "Garlic"


class Spinach(Veggies):
    def __str__(self) -> str:
        return "Spinach"


class Mushroom(Veggies):
    def __str__(self) -> str:
        return "Mushrooms"


class Eggplant(Veggies):
    def __str__(self) -> str:
        return "Eggplant"


class RedPepper(Veggies):
    def __str__(self) -> str:
        return "Red Pepper"


class BlackOlives(Veggies):
    def __str__(self) -> str:
        return "Black Olives"
