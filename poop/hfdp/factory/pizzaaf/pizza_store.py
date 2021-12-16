from abc import ABC, abstractmethod

from poop.hfdp.factory.pizzaaf.pizza import Pizza


class PizzaStore(ABC):
    @abstractmethod
    def create_pizza(self, flavor: str) -> Pizza | None:
        raise NotImplementedError

    def order_pizza(self, flavor: str) -> Pizza:
        pizza: Pizza | None = self.create_pizza(flavor)
        if pizza is None:
            raise ValueError(f"Invalid pizza flavor: {flavor}")

        print(f"--- Making a {pizza.get_name()} ---")
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza
