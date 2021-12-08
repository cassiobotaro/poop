from poop.hfdp.factory.pizzas.pizza import Pizza


class PepperoniPizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self._name = "Pepperoni Pizza"
        self._dough = "Crust"
        self._sauce = "Marinara sauce"
        self._toppings.append("Sliced Pepperoni")
        self._toppings.append("Sliced Onion")
        self._toppings.append("Grated parmesan cheese")
