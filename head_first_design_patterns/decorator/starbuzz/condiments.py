from abc import abstractmethod

from beverages import Beverage

"""
NOTES:
    - Instead of use inheritance and made a lot of combinations of
    beverages and condiments we use decorator pattern
    - CondimentDecorator is a wrapper of a Beverage, using composition
    and delegation to achieve flexibility
    - Each CondimentDecorator subclasses, should implement get_description
    and cost
    - We delegate to our wrapped class do some behaviours and then we
    make some modifiations
    - Be careful, this pattern can result in a lot of small objects and
    increase complexity
    - A condiment represents a beverage with that condiment. For example, a
    milk classs doesn't represents a cup of milk, but a beverage with milk.
"""


class CondimentDecorator(Beverage):
    def __init__(self, beverage):
        self.beverage = beverage

    @abstractmethod
    def get_description(self):
        raise NotImplementedError

    def get_size(self):
        return self.beverage.get_size()


class Milk(CondimentDecorator):
    def get_description(self):
        return self.beverage.get_description() + ", Milk"

    def cost(self):
        return self.beverage.cost() + 0.10


class Mocha(CondimentDecorator):
    def get_description(self):
        return self.beverage.get_description() + ", Mocha"

    def cost(self):
        return self.beverage.cost() + 0.20


class Soy(CondimentDecorator):
    def get_description(self):
        return self.beverage.get_description() + ", Soy"

    def cost(self):
        condiment_cost = {
            self.beverage.size.TALL: 0.10,
            self.beverage.size.GRANDE: 0.15,
            self.beverage.size.VENTI: 0.20,
        }[self.beverage.get_size()]
        return self.beverage.cost() + condiment_cost


class Whip(CondimentDecorator):
    def get_description(self):
        return self.beverage.get_description() + ", Whip"

    def cost(self):
        return 0.10 + self.beverage.cost()
