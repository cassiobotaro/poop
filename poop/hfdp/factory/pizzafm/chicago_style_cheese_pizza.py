from poop.hfdp.factory.pizzafm.pizza import Pizza


class ChicagoStyleCheesePizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Chicago Style Deep Dish Cheese Pizza"
        self.dough = "Extra Thick Crust Dough"
        self.sauce = "Plum Tomato Sauce"

        self.toppings.append("Shredded Mozzarella Cheese")

    def cut(self) -> None:
        print("Cutting the pizza into square slices")
