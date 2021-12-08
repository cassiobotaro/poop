from poop.hfdp.factory.pizzas.pizza import Pizza


class CheesePizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self._name = "Cheese Pizza"
        self._dough = "Regular Crust"
        self._sauce = "Marinara Pizza Sauce"
        self._toppings.append("Fresh Mozzarella")
        self._toppings.append("Parmesan")
