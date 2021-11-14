"""
Notes:
    - Each cheese has its own str representation
    - Each ingredient is a product that is produced
    by a Factory Method (create_cheese)
    in the Abstract Factory (PizzaIngredientFactory)
    See pizza_ingredient_factory.py
"""
from abc import ABC, abstractmethod


class Cheese(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class ParmesanCheese(Cheese):
    def __str__(self) -> str:
        return "Shredded Parmesan"


class ReggianoCheese(Cheese):
    def __str__(self) -> str:
        return "Reggiano Cheese"


class MozzarellaCheese(Cheese):
    def __str__(self) -> str:
        return "Shredded Mozzarella"
