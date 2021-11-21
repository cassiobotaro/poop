from abc import ABC, abstractmethod

from poop.hfdp.decorator.pizza.pizza import Pizza


class ToppingDecorator(Pizza, ABC):
    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError
