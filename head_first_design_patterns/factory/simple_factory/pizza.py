"""
Notes:
    - use ABC to formalize that is an abstract method
    - only inheriting from ABC does not guarantee that it cannot be
    instantiated
    - @abstractmethod on __init__ guarantees that the class cannot be
    instantiated, only your specialization

    - super().__init__() guarantees that the instance have all
    required attributes
    - we are in the pizza namespace, Pizza sufix is redundant
    - Each pizza has its own characteristics

    when I ran mypy, I got a lot of errors, so I decided to create an
    invalid flavor pizza, respecting the pizza type interface.
    It's a Null object Pattern.
    Helps to avoid multiple ifs (including exceptions) when an item is not
    found.
"""
from abc import ABC, abstractmethod


class Pizza(ABC):
    @abstractmethod
    def __init__(self):
        self.name: str = ""
        self.dough: str = ""
        self.sauce: str = ""
        self.toppings: list[str] = []

    def get_name(self) -> str:
        return self.name

    def prepare(self) -> None:
        print(f"Preparing {self.name}")

    def bake(self) -> None:
        print(f"Baking {self.name}")

    def cut(self) -> None:
        print(f"Cutting {self.name}")

    def box(self) -> None:
        print(f"Boxing {self.name}")

    def __str__(self) -> str:
        joined_toppings = "\n".join(self.toppings)
        return (
            f"---- {self.name} ----\n"
            f"{self.dough}\n"
            f"{self.sauce}\n"
            f"{joined_toppings}\n"
        )


class UnknownPizza(Pizza):
    def __init__(self):
        self.name = "unknow flavor"


class CheesePizza(Pizza):
    def __init__(self):
        super().__init__()
        self.name = "Cheese Pizza"
        self.doough = "Regular Crust"
        self.sauce = "Marinara Pizza Sauce"
        self.toppings.append("Fresh Mozzarella")
        self.toppings.append("Parmesan")


class ClamPizza(Pizza):
    def __init__(self):
        super().__init__()
        self.name = "Clam Pizza"
        self.doough = "Thin Crust"
        self.sauce = "White garlic sauce"
        self.toppings.append("Clams")
        self.toppings.append("Grated parmesan cheese")


class VeggiePizza(Pizza):
    def __init__(self):
        super().__init__()
        self.name = "Veggie Pizza"
        self.dough = "Crust"
        self.sauce = "Marinara sauce"
        self.toppings.append("Shredded mozzarella")
        self.toppings.append("Grated parmesan")
        self.toppings.append("Diced onion")
        self.toppings.append("Sliced mushrooms")
        self.toppings.append("Sliced red pepper")
        self.toppings.append("Sliced black olives")


class PepperoniPizza(Pizza):
    def __init__(self):
        super().__init__()
        self.name = "Pepperoni Pizza"
        self.dough = "Crust"
        self.sauce = "Marinara sauce"
        self.toppings.append("Sliced Pepperoni")
        self.toppings.append("Sliced Onion")
        self.toppings.append("Grated parmesan cheese")
