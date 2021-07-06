from beverages import Beverage, DarkRoast, Decaf, Espresso, HouseBlend
from condiments import Milk, Mocha, Soy, Whip

# beverages have description and cost
beverage = Espresso()
print(f"{beverage.get_description()} ${beverage.cost():2.2f}")

# wrap beverages with condiments
beverage2: Beverage = DarkRoast()
beverage2 = Mocha(beverage2)
beverage2 = Mocha(beverage2)
beverage2 = Whip(beverage2)
print(f"{beverage2.get_description()} ${beverage2.cost():2.2f}")

# Soy for example use size to set a cost
beverage3: Beverage = HouseBlend()
beverage3.set_size(beverage3.SIZE.VENTI)
beverage3 = Soy(beverage3)
beverage3 = Mocha(beverage3)
beverage3 = Whip(beverage3)
print(f"{beverage3.get_description()} ${beverage3.cost():2.2f}")

# Decaf with milk, blergh!
beverage4: Beverage = Decaf()
beverage4 = Milk(beverage4)
print(f"{beverage4.get_description()} ${beverage4.cost():2.2f}")
