from abc import abstractmethod

"""
NOTES:
    - Thickcrust and Thincrust are pizza, changing description and implement
    your own price
    - description in class Pizza is used as a default
    - As an abstract method, cost should be implemented by subclasses.
    It is used to formalize a contract between subclasses.
"""


class Pizza:
    description = "Basic Pizza"

    def get_description(self):
        return self.description

    @abstractmethod
    def cost(self):
        raise NotImplementedError


class ThickcrustPizza(Pizza):
    def __init__(self):
        self.description = "Thick crust pizza, with tomato sauce"

    def cost(self):
        return 7.99


class ThincrustPizza(Pizza):
    def __init__(self):
        self.description = "Thin crust pizza, with tomato sauce"

    def cost(self):
        return 7.99
