from poop.hfdp.factory.pizzafm.chicago_style_cheese_pizza import (
    ChicagoStyleCheesePizza,
)
from poop.hfdp.factory.pizzafm.chicago_style_clam_pizza import (
    ChicagoStyleClamPizza,
)
from poop.hfdp.factory.pizzafm.chicago_style_pepperoni_pizza import (
    ChicagoStylePepperoniPizza,
)
from poop.hfdp.factory.pizzafm.chicago_style_veggie_pizza import (
    ChicagoStyleVeggiePizza,
)
from poop.hfdp.factory.pizzafm.pizza import Pizza
from poop.hfdp.factory.pizzafm.pizza_store import PizzaStore


class ChicagoPizzaStore(PizzaStore):
    def create_pizza(self, flavor: str) -> Pizza | None:
        if flavor == "cheese":
            return ChicagoStyleCheesePizza()
        elif flavor == "veggie":
            return ChicagoStyleVeggiePizza()
        elif flavor == "clam":
            return ChicagoStyleClamPizza()
        elif flavor == "pepperoni":
            return ChicagoStylePepperoniPizza()
        return None
