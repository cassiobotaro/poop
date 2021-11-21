from poop.hfdp.decorator.starbuzz_with_sizes.condiment_decorator import (
    CondimentDecorator,
)


class Whip(CondimentDecorator):
    def get_description(self) -> str:
        return self.beverage.get_description() + ", Whip"

    def cost(self) -> float:
        return 0.10 + self.beverage.cost()
