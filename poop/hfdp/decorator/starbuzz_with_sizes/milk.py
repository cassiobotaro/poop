from poop.hfdp.decorator.starbuzz_with_sizes.condiment_decorator import (
    CondimentDecorator,
)


class Milk(CondimentDecorator):
    def get_description(self) -> str:
        return self.beverage.get_description() + ", Milk"

    def cost(self) -> float:
        return self.beverage.cost() + 0.10
