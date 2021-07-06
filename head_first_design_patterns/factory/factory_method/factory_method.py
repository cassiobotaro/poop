"""
Notes:
    - The method is defined in an abstract way, so it can be specialized with
    what varies (object creation)
    - Store classes inherit from abstract classes
    - pass the flavour (str) to a fabric and wait for a pizza
"""
from fm_pizza import Pizza
from fm_pizza_store import ChicagoPizzaStore, NYPizzaStore

ny_store: NYPizzaStore = NYPizzaStore()
chicago_store: ChicagoPizzaStore = ChicagoPizzaStore()

pizza: Pizza = ny_store.order_pizza("cheese")
print(f"Ethan ordered a {pizza.get_name()}")

pizza = chicago_store.order_pizza("cheese")
print(f"Joel ordered a {pizza.get_name()}")

pizza = ny_store.order_pizza("clam")
print(f"Ethan ordered a {pizza.get_name()}")

pizza = chicago_store.order_pizza("clam")
print(f"Joel ordered a {pizza.get_name()}")

pizza = ny_store.order_pizza("pepperoni")
print(f"Ethan ordered a {pizza.get_name()}")

pizza = chicago_store.order_pizza("pepperoni")
print(f"Joel ordered a {pizza.get_name()}")

pizza = ny_store.order_pizza("veggie")
print(f"Ethan ordered a {pizza.get_name()}")

pizza = chicago_store.order_pizza("veggie")
print(f"Joel ordered a {pizza.get_name()}")
