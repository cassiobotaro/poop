"""
Notes:
    - store is created based on factory who controls which pizzas are available
    - Our client class (PizzaStore) doesn't need to know the creation of
    concrete objects, that is, it dependence is of the abstract Pizza type
    - pass the flavour (str) to a fabric and wait for a pizza
    - simple factories may not be considered a design pattern
"""
from pizza import Pizza
from pizza_factory import SimplePizzaFactory
from pizza_store import PizzaStore

store: PizzaStore = PizzaStore(SimplePizzaFactory())

pizza: Pizza = store.order_pizza("cheese")
print(f"We ordered a {pizza.get_name()}")
print(pizza)

pizza = store.order_pizza("veggie")
print(f"We ordered a {pizza.get_name()}")
print(pizza)

pizza = store.order_pizza("clam")
print(f"We ordered a {pizza.get_name()}")
print(pizza)

pizza = store.order_pizza("pepperoni")
print(f"We ordered a {pizza.get_name()}")
print(pizza)
