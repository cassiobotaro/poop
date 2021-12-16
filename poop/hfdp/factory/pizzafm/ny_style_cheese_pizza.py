from poop.hfdp.factory.pizzafm.pizza import Pizza


class NYStyleCheesePizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self.name = "NY Style Sauce and Cheese Pizza"
        self.dough = "Thin Crust Dough"
        self.sauce = "Marinara Sauce"

        self.toppings.append("Grated Reggiano Cheese")
