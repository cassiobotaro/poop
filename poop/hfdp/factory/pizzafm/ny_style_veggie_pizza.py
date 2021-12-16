from poop.hfdp.factory.pizzafm.pizza import Pizza


class NYStyleVeggiePizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self.name = "NY Style Veggie Pizza"
        self.dough = "Thin Crust Dough"
        self.sauce = "Marinara Sauce"

        self.toppings.append("Grated Reggiano Cheese")
        self.toppings.append("Garlic")
        self.toppings.append("Onion")
        self.toppings.append("Mushrooms")
        self.toppings.append("Red Pepper")
