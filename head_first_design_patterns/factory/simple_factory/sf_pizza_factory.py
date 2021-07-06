"""
Notes:
    - return pizza based on flavor, or unknown pizza
    - remove creation logic from Pizza
    - factory contains logic to create products (Pizza)
"""
from sf_pizza import (
    CheesePizza,
    ClamPizza,
    PepperoniPizza,
    Pizza,
    UnknownPizza,
    VeggiePizza,
)


class SimplePizzaFactory:
    def create_pizza(self, flavor: str) -> Pizza:
        if flavor == "cheese":
            return CheesePizza()
        elif flavor == "clam":
            return ClamPizza()
        elif flavor == "veggie":
            return VeggiePizza()
        elif flavor == "pepperoni":
            return PepperoniPizza()
        return UnknownPizza()
