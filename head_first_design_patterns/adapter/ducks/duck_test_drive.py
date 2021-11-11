"""Notes:
- Adapter is a pattern that allows classes to work together
that weren't designed to work together.
"""
from adapters import TurkeyAdapter
from drones import Drone, DroneAdapter, SuperDrone
from ducks import Duck, MallardDuck
from turkeys import Turkey, WildTurkey


def test_duck(duck: Duck) -> None:
    duck.quack()
    duck.fly()


# Note: Using variables of type defined by protocols instead of concrete types
duck: Duck = MallardDuck()
turkey: Turkey = WildTurkey()
turkey_adapter: Duck = TurkeyAdapter(turkey)

print("The turkey says...")
turkey.gobble()
turkey.fly()

print("The Duck says")
test_duck(duck)

# Note: A turkey adapter communicates through the duck interface
print("The TurkeyAdapter says...")
test_duck(turkey_adapter)

# Challenge
drone: Drone = SuperDrone()
# note: a drone adapter communicates through the duck interface
drone_adapter: Duck = DroneAdapter(drone)
test_duck(drone_adapter)
