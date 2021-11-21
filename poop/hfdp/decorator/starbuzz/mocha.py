from poop.hfdp.decorator.starbuzz.condiment_decorator import CondimentDecorator


class Mocha(CondimentDecorator):
    def get_description(self) -> str:
        return self.beverage.get_description() + ", Mocha"

    def cost(self) -> float:
        return self.beverage.cost() + 0.20
