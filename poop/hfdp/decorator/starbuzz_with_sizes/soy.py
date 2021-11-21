from poop.hfdp.decorator.starbuzz_with_sizes.beverage import Beverage
from poop.hfdp.decorator.starbuzz_with_sizes.condiment_decorator import (
    CondimentDecorator,
)


class Soy(CondimentDecorator):
    def get_description(self) -> str:
        return self.beverage.get_description() + ", Soy"

    def cost(self) -> float:
        condiment_cost = {
            Beverage.SIZE.TALL: 0.10,
            Beverage.SIZE.GRANDE: 0.15,
            Beverage.SIZE.VENTI: 0.20,
        }[self.beverage.get_size()]
        return self.beverage.cost() + condiment_cost
