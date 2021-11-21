from poop.hfdp.decorator.starbuzz_with_sizes.beverage import Beverage
from poop.hfdp.decorator.starbuzz_with_sizes.dark_roast import DarkRoast
from poop.hfdp.decorator.starbuzz_with_sizes.espresso import Espresso
from poop.hfdp.decorator.starbuzz_with_sizes.house_blend import HouseBlend
from poop.hfdp.decorator.starbuzz_with_sizes.mocha import Mocha
from poop.hfdp.decorator.starbuzz_with_sizes.soy import Soy
from poop.hfdp.decorator.starbuzz_with_sizes.whip import Whip


def main() -> None:
    beverage: Beverage = Espresso()
    print(f"{beverage.get_description()} ${beverage.cost():2.2f}")

    beverage2: Beverage = DarkRoast()
    beverage2 = Mocha(beverage2)
    beverage2 = Mocha(beverage2)
    beverage2 = Whip(beverage2)
    print(f"{beverage2.get_description()} ${beverage2.cost():2.2f}")

    beverage3: Beverage = HouseBlend()
    beverage3.set_size(Beverage.SIZE.VENTI)
    beverage3 = Soy(beverage3)
    beverage3 = Mocha(beverage3)
    beverage3 = Whip(beverage3)
    print(f"{beverage3.get_description()} ${beverage3.cost():2.2f}")
