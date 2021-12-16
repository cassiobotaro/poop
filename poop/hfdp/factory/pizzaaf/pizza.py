from abc import ABC, abstractmethod

from poop.hfdp.factory.pizzaaf.cheese import Cheese
from poop.hfdp.factory.pizzaaf.clams import Clams
from poop.hfdp.factory.pizzaaf.dough import Dough
from poop.hfdp.factory.pizzaaf.pepperoni import Pepperoni
from poop.hfdp.factory.pizzaaf.sauce import Sauce
from poop.hfdp.factory.pizzaaf.veggies import Veggies


class Pizza(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.name: str = ""

        self.dough: Dough | None = None
        self.sauce: Sauce | None = None
        self.veggies: list[Veggies] = []
        self.cheese: Cheese | None = None
        self.pepperoni: Pepperoni | None = None
        self.clams: Clams | None = None

    @abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError

    def bake(self) -> None:
        print("Bake for 25 minutes at 350")

    def cut(self) -> None:
        print("Cut the pizza into diagonal slices")

    def box(self) -> None:
        print("Place pizza in official PizzaStore box")

    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        dough = f"{self.dough}\n" if self.dough else ""
        sauce = f"{self.sauce}\n" if self.sauce else ""
        cheese = f"{self.cheese}\n" if self.cheese else ""
        veggies = (
            ",".join(str(veggie) for veggie in self.veggies) + "\n"
            if self.veggies
            else ""
        )
        clam = f"{self.clams}\n" if self.clams else ""
        pepperoni = f"{self.pepperoni}\n" if self.pepperoni else ""
        return (
            f"---- {self.name} ----\n"
            f"{dough}"
            f"{sauce}"
            f"{cheese}"
            f"{veggies}"
            f"{clam}"
            f"{pepperoni}"
        )
