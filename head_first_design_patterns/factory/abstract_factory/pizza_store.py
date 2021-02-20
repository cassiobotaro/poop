"""
Notes:
    - useful in creating product families, example custom cheese pizza
      from new york
      that is, the pizzas created are of the same quality,
      but the flavor varies according to the factory and
      the ingredients are different
    - one thing i noticed is that with this abstraction the chicago cut which
      was square didn’t remain
    - each store depends on the abstraction of a factory of ingradientes and
      not something concrete
    - the create_pizza method is a method that behaves
      like a factory (factory method)
    - the PizzaStore type has the factory method that is implemented depending
      on an abstraction of the ingradients factory (see NYPizzaStore)
      which in turn uses a method as a factory that depends on
      abstractions of each of the ingredients 🤯
    - UnknownPizza implements the abstraction of a Pizza,
      eliminating several if's in the implementation

"""
from abc import ABC, abstractmethod

from pizza import (
    CheesePizza,
    ClamPizza,
    PepperoniPizza,
    Pizza,
    UnknownPizza,
    VeggiePizza,
)
from pizza_ingredient_factory import (
    ChicagoPizzaIngredientFactory,
    NYPizzaIngredientFactory,
    PizzaIngredientFactory,
)


class PizzaStore(ABC):
    @abstractmethod
    def create_pizza(self, flavor: str) -> Pizza:
        raise NotImplementedError

    def order_pizza(self, flavor: str) -> Pizza:
        pizza: Pizza = self.create_pizza(flavor)
        print(f"--- Making a {pizza.get_name()} ---")
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza


class NYPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza:
        ingredient_factory: PizzaIngredientFactory = NYPizzaIngredientFactory()
        pizza: Pizza = UnknownPizza()
        if flavor == "cheese":
            pizza = CheesePizza(ingredient_factory)
            pizza.set_name("New York Style Cheese Pizza")
        elif flavor == "veggie":
            pizza = VeggiePizza(ingredient_factory)
            pizza.set_name("New York Style Veggie Pizza")
        elif flavor == "clam":
            pizza = ClamPizza(ingredient_factory)
            pizza.set_name("New York Style Clam Pizza")
        elif flavor == "pepperoni":
            pizza = PepperoniPizza(ingredient_factory)
            pizza.set_name("New York Style Pepperoni Pizza")
        return pizza


class ChicagoPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza:
        ingredient_factory: PizzaIngredientFactory = (
            ChicagoPizzaIngredientFactory()
        )
        pizza: Pizza = UnknownPizza()
        if flavor == "cheese":
            pizza = CheesePizza(ingredient_factory)
            pizza.set_name("Chicago Style Cheese Pizza")
        elif flavor == "veggie":
            pizza = VeggiePizza(ingredient_factory)
            pizza.set_name("Chicago Style Veggie Pizza")
        elif flavor == "clam":
            pizza = ClamPizza(ingredient_factory)
            pizza.set_name("Chicago Style Clam Pizza")
        elif flavor == "pepperoni":
            pizza = PepperoniPizza(ingredient_factory)
            pizza.set_name("Chicago Style Pepperoni Pizza")
        return pizza
