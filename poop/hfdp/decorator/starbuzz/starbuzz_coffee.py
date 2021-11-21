from poop.hfdp.decorator.starbuzz.beverage import Beverage
from poop.hfdp.decorator.starbuzz.espresso import Espresso
from poop.hfdp.decorator.starbuzz.house_blend import HouseBlend
from poop.hfdp.decorator.starbuzz.mocha import Mocha
from poop.hfdp.decorator.starbuzz.soy import Soy
from poop.hfdp.decorator.starbuzz.whip import Whip


def main() -> None:
    beverage: Beverage = Espresso()
    print(f"{beverage.get_description()} ${beverage.cost():2.2f}")

    beverage = HouseBlend()
    beverage = Soy(beverage)
    beverage = Mocha(beverage)
    beverage = Whip(beverage)
    print(beverage.get_description())
    print(beverage.cost())
