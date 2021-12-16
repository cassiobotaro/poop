from abc import ABC, abstractmethod


class Pizza(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.name: str = ""
        self.dough: str = ""
        self.sauce: str = ""
        self.toppings: list[str] = []

    def prepare(self) -> None:
        print(f"Prepare {self.name}")
        print("Tossing dough...")
        print("Adding sauce...")
        print("Adding toppings:")
        for topping in self.toppings:
            print(f" {topping}")

    def get_name(self) -> str:
        return self.name

    def bake(self) -> None:
        print("Bake for 25 minutes at 350")

    def cut(self) -> None:
        print("Cut the pizza into diagonal slices")

    def box(self) -> None:
        print("Place pizza in official PizzaStore box")

    def __str__(self) -> str:
        joined_toppings = "\n".join(self.toppings)
        return (
            f"---- {self.name} ----\n"
            f"{self.dough}\n"
            f"{self.sauce}\n"
            f"{joined_toppings}\n"
        )
