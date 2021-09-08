from adapters import TurkeyAdapter
from drones import Drone, DroneAdapter, SuperDrone
from ducks import Duck, MallardDuck
from turkeys import Turkey, WildTurkey


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
