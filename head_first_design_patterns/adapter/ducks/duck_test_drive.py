from head_first_design_patterns.adapter.ducks.challenge.drone import Drone
from head_first_design_patterns.adapter.ducks.challenge.drone_adapter import (
    DroneAdapter,
)
from head_first_design_patterns.adapter.ducks.challenge.super_drone import (
    SuperDrone,
)
from head_first_design_patterns.adapter.ducks.duck import Duck
from head_first_design_patterns.adapter.ducks.mallard_duck import MallardDuck
from head_first_design_patterns.adapter.ducks.turkey import Turkey
from head_first_design_patterns.adapter.ducks.turkey_adapter import (
    TurkeyAdapter,
)
from head_first_design_patterns.adapter.ducks.wild_turkey import WildTurkey


def test_duck(duck: Duck) -> None:
    duck.quack()
    duck.fly()


duck: Duck = MallardDuck()
turkey: Turkey = WildTurkey()
turkey_adapter: Duck = TurkeyAdapter(turkey)

print("The turkey says...")
turkey.gobble()
turkey.fly()

print("The Duck says")
test_duck(duck)

print("The TurkeyAdapter says...")
test_duck(turkey_adapter)

# Challenge
drone: Drone = SuperDrone()
drone_adapter: Duck = DroneAdapter(drone)
test_duck(drone_adapter)
