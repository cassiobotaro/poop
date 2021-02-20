"""
Notes:
    - PizzaStore is abstract, your subclasses must implement their
    abstract methods
    - Each store define your own METHOD to create a pizza. This method
    works like a factory and generate products (Pizza)
    - You can specialize and custom factory, deciding which flavors and styles
    are the pizza you make
"""
from abc import ABC, abstractmethod

from pizza import (
    ChicagoStyleCheesePizza,
    ChicagoStyleClamPizza,
    ChicagoStylePepperoniPizza,
    ChicagoStyleVeggiePizza,
    NYStyleCheesePizza,
    NYStyleClamPizza,
    NYStylePepperoniPizza,
    NYStyleVeggiePizza,
    Pizza,
    UnknownPizza,
)


class PizzaStore(ABC):
    @abstractmethod
    def create_pizza(self, flavor: str) -> Pizza:
        raise NotImplementedError

    def order_pizza(self, flavor: str) -> Pizza:
        pizza = self.create_pizza(flavor)
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza


class ChicagoPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza:
        if flavor == "cheese":
            return ChicagoStyleCheesePizza()
        elif flavor == "veggie":
            return ChicagoStyleVeggiePizza()
        elif flavor == "clam":
            return ChicagoStyleClamPizza()
        elif flavor == "pepperoni":
            return ChicagoStylePepperoniPizza()
        return UnknownPizza()


class NYPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza:
        if flavor == "cheese":
            return NYStyleCheesePizza()
        elif flavor == "veggie":
            return NYStyleVeggiePizza()
        elif flavor == "clam":
            return NYStyleClamPizza()
        elif flavor == "pepperoni":
            return NYStylePepperoniPizza()
        return UnknownPizza()
