from poop.hfdp.decorator.pizza.pizza import Pizza


class ThincrustPizza(Pizza):
    def __init__(self) -> None:
        self.description = "Thin crust pizza, with tomato sauce"

    def cost(self) -> float:
        return 7.99
