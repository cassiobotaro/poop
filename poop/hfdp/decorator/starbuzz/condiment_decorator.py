from abc import ABC, abstractmethod

from poop.hfdp.decorator.starbuzz.beverage import Beverage


class CondimentDecorator(Beverage, ABC):
    def __init__(self, beverage: Beverage):
        self.beverage = beverage

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError
