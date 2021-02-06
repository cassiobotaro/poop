from abc import abstractmethod

from pizza import Pizza
"""
Notes:
    - cheese and olives are toppings, they implement get_description
    because of Topping interface and also cost because of Pizza interface
    - imagine that a topping decorator represents a pizza with that topping
    - we MODIFY cost and description, adding things
    - Inheritance is used to close a deal
"""


class ToppingDecorator(Pizza):
    def __init__(self, pizza):
        self.pizza = pizza

    @abstractmethod
    def get_description(self):
        raise NotImplementedError


class Cheese(ToppingDecorator):

    def get_description(self):
        return self.pizza.get_description() + ', Cheese'

    def cost(self):
        return self.pizza.cost()  # cheese is free


class Olives(ToppingDecorator):

    def get_description(self):
        return self.pizza.get_description() + ', Olives'

    def cost(self):
        return self.pizza.cost() + .30
