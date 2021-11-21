from poop.hfdp.decorator.pizza.pizza import Pizza


class ThickcrustPizza(Pizza):
    def __init__(self) -> None:
        self.description = "Thick crust pizza, with tomato sauce"

    def cost(self) -> float:
        return 7.99
