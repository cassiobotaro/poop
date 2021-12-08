from abc import ABC


class Pizza(ABC):
    def __init__(self) -> None:
        self._name: str = ""
        self._dough: str = ""
        self._sauce: str = ""
        self._toppings: list[str] = []

    def get_name(self) -> str:
        return self._name

    def prepare(self) -> None:
        print(f"Preparing {self._name}")

    def bake(self) -> None:
        print(f"Baking {self._name}")

    def cut(self) -> None:
        print(f"Cutting {self._name}")

    def box(self) -> None:
        print(f"Boxing {self._name}")

    def __str__(self) -> str:
        joined_toppings = "\n".join(self._toppings)
        return (
            f"---- {self._name} ----\n"
            f"{self._dough}\n"
            f"{self._sauce}\n"
            f"{joined_toppings}\n"
        )
