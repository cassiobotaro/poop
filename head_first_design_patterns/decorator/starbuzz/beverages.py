from abc import abstractmethod
from enum import Enum
"""
Notes:
    - enum SIZE represents allowed sizes of BEVERAGE
    - size is a default size for Beverages and each instance
    can change it using set_size
    - cost is the unique method to be implemented, but you also
    will want to change the description
"""


class Beverage:
    SIZE = Enum('SIZE', 'TALL GRANDE VENTI')

    size = SIZE.TALL
    description = "Unknown Beverage"

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.size

    def get_description(self):
        return self.description

    @abstractmethod
    def cost(self):
        raise NotImplementedError


class DarkRoast(Beverage):
    def __init__(self):
        self.description = "Dark Roast Coffee"

    def cost(self):
        return .99


class Decaf(Beverage):
    def __init__(self):
        self.description = "Decaf Coffee"

    def cost(self):
        return 1.05


class Espresso(Beverage):
    def __init__(self):
        self.description = "Espresso Coffee"

    def cost(self):
        return 1.99


class HouseBlend(Beverage):
    def __init__(self):
        self.description = "House Blend Coffee"

    def cost(self):
        return .89
