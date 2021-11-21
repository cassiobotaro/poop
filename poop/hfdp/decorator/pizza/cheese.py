from poop.hfdp.decorator.pizza.topping_decorator import ToppingDecorator


class Cheese(ToppingDecorator):
    def get_description(self) -> str:
        return self.pizza.get_description() + ", Cheese"

    def cost(self) -> float:
        return self.pizza.cost()  # queijo é grátis
