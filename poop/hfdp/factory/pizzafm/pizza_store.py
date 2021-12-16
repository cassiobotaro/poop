from abc import ABC, abstractmethod

from poop.hfdp.factory.pizzafm.pizza import Pizza


class PizzaStore(ABC):
    @abstractmethod
    def create_pizza(self, flavor: str) -> Pizza | None:
        raise NotImplementedError

    def order_pizza(self, flavor: str) -> Pizza:
        pizza = self.create_pizza(flavor)
        if pizza is None:
            raise ValueError(f"Invalid pizza flavor: {flavor}")
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza
