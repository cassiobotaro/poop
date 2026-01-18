"""
Notes:
    - attributes are prefixed with "__" to avoid accidental changes (private?)
    - different from the java version, the definition of creating a
    single instance is in the metaclass (class used to create the class)
    - Chocolate Boiler has it own attributes and behaviors
"""

from .classic import SingletonMeta


class ChocolateBoiler(metaclass=SingletonMeta):
    def __init__(self):
        self.__empty = True
        self.__boiled = False

    def fill(self):
        if self.is_empty():
            self.__empty = False
            self.__boiled = False
            # fill the boiler with a milk/chocolate mixture

    def drain(self):
        if not self.is_empty() and self.is_boiled():
            # drain the boiled milk and chocolate
            self.__empty = True

    def boil(self):
        if not self.is_empty() and not self.is_boiled():
            # bring the contents to a boil
            self.__boiled = True

    def is_empty(self):
        return self.__empty

    def is_boiled(self):
        return self.__boiled


# We don't need a special method to instantiate a unique chocolate boiler
boiler = ChocolateBoiler()
boiler.fill()
boiler.boil()
boiler.drain()

# will return the existing instance
boiler2 = ChocolateBoiler()

print(f"{id(boiler)=} == {id(boiler2)=}")
