from poop.hfdp.factory.pizzas.pizza import Pizza


class ClamPizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self._name = "Clam Pizza"
        self._doough = "Thin Crust"
        self._sauce = "White garlic sauce"
        self._toppings.append("Clams")
        self._toppings.append("Grated parmesan cheese")
