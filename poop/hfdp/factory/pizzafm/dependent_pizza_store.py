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
from poop.hfdp.factory.pizzafm.ny_style_cheese_pizza import NYStyleCheesePizza
from poop.hfdp.factory.pizzafm.ny_style_clam_pizza import NYStyleClamPizza
from poop.hfdp.factory.pizzafm.ny_style_pepperoni_pizza import (
    NYStylePepperoniPizza,
)
from poop.hfdp.factory.pizzafm.ny_style_veggie_pizza import NYStyleVeggiePizza
from poop.hfdp.factory.pizzafm.pizza import Pizza


class DependentPizzaStore:
    def create_pizza(self, style: str, kind: str) -> Pizza | None:
        pizza: Pizza | None = None
        if style == "NY":
            if kind == "cheese":
                pizza = NYStyleCheesePizza()
            elif kind == "veggie":
                pizza = NYStyleVeggiePizza()
            elif kind == "clam":
                pizza = NYStyleClamPizza()
            elif kind == "pepperoni":
                pizza = NYStylePepperoniPizza()
        elif style == "Chicago":
            if kind == "cheese":
                pizza = ChicagoStyleCheesePizza()
            elif kind == "veggie":
                pizza = ChicagoStyleVeggiePizza()
            elif kind == "clam":
                pizza = ChicagoStyleClamPizza()
            elif kind == "pepperoni":
                pizza = ChicagoStylePepperoniPizza()

        if pizza is None:
            print("Error: invalid type of pizza")
            return None

        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza
