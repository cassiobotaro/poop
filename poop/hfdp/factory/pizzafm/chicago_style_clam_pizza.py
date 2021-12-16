from poop.hfdp.factory.pizzafm.pizza import Pizza


class ChicagoStyleClamPizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Chicago Style Clam Pizza"
        self.doough = "Extra Thick Crust Dough"
        self.sauce = "Plum Tomato Sauce"
        self.toppings.append("Shredded Mozzarella Cheese")
        self.toppings.append("Frozen Clams from Chesapeake Bay")

    def cut(self) -> None:
        print("Cutting the pizza into square slices")
