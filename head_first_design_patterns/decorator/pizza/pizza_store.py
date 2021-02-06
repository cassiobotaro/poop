from pizza import ThickcrustPizza, ThincrustPizza
from topping import Cheese, Olives


# create a pizza
pizza = ThincrustPizza()
# decorate with free cheese
cheese_pizza = Cheese(pizza)
# decorate again using Olives
# It's possible because topping respect pizza interface
greek_pizza = Olives(pizza)
print(f"{greek_pizza.get_description()} ${greek_pizza.cost():2.2f}")

# create other pizza...just to use all classes!
pizza2 = ThickcrustPizza()
print(f"{pizza2.get_description()} ${pizza2.cost():2.2f}")
