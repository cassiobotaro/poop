from poop.hfdp.decorator.pizza.cheese import Cheese
from poop.hfdp.decorator.pizza.olives import Olives
from poop.hfdp.decorator.pizza.thickcrust_pizza import ThickcrustPizza
from poop.hfdp.decorator.pizza.thincrust_pizza import ThincrustPizza


def main() -> None:
    # cria uma pizza
    pizza = ThincrustPizza()
    # decora com queijo grátis
    cheese_pizza = Cheese(pizza)
    print(f"{cheese_pizza.get_description()} ${cheese_pizza.cost():2.2f}")
    # decora novamente usando azeitonas
    # Isto é possível porque o ToppingDecorator respeita a interface Pizza
    greek_pizza = Olives(pizza)
    print(f"{greek_pizza.get_description()} ${greek_pizza.cost():2.2f}")

    # criando outra pizza...apenas para usar todas as classes!
    pizza2 = ThickcrustPizza()
    print(f"{pizza2.get_description()} ${pizza2.cost():2.2f}")
