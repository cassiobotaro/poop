from poop.hfdp.decorator.pizza.topping_decorator import ToppingDecorator


class Olives(ToppingDecorator):
    def get_description(self) -> str:
        return self.pizza.get_description() + ", Olives"

    def cost(self) -> float:
        return self.pizza.cost() + 0.30
