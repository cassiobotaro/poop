from abc import ABC, abstractmethod

from poop.hfdp.decorator.starbuzz_with_sizes.beverage import Beverage


class CondimentDecorator(Beverage, ABC):
    def __init__(self, beverage: Beverage):
        self.beverage = beverage

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError

    def get_size(self) -> Beverage.SIZE:
        return self.beverage.get_size()
