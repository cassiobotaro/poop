"""
Notes:
    - We use the factories, without needing to know their internal behavior
    - We only call the method "order_pizza" which is the common
    interface of pizza factories
    - A pizza is an abstraction of a pizza of a certain flavor,
    with its respective ingredients
"""
from pizza import Pizza
from pizza_store import ChicagoPizzaStore, NYPizzaStore, PizzaStore

ny_store: PizzaStore = NYPizzaStore()
chicago_store: PizzaStore = ChicagoPizzaStore()

pizza: Pizza = ny_store.order_pizza("cheese")
print(f"Ethan ordered a {pizza.get_name()}")

pizza = chicago_store.order_pizza("chease")
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
