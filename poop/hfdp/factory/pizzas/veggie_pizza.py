from poop.hfdp.factory.pizzas.pizza import Pizza


class VeggiePizza(Pizza):
    def __init__(self) -> None:
        super().__init__()
        self._name = "Veggie Pizza"
        self._dough = "Crust"
        self._sauce = "Marinara sauce"
        self._toppings.append("Shredded mozzarella")
        self._toppings.append("Grated parmesan")
        self._toppings.append("Diced onion")
        self._toppings.append("Sliced mushrooms")
        self._toppings.append("Sliced red pepper")
        self._toppings.append("Sliced black olives")
