from poop.hfdp.decorator.starbuzz.condiment_decorator import CondimentDecorator


class Soy(CondimentDecorator):
    def get_description(self) -> str:
        return self.beverage.get_description() + ", Soy"

    def cost(self) -> float:
        return self.beverage.cost() + 0.15
