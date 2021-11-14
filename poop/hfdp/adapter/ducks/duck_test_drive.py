from poop.hfdp.adapter.ducks.challenge.drone import Drone
from poop.hfdp.adapter.ducks.challenge.drone_adapter import DroneAdapter
from poop.hfdp.adapter.ducks.challenge.super_drone import SuperDrone
from poop.hfdp.adapter.ducks.duck import Duck
from poop.hfdp.adapter.ducks.mallard_duck import MallardDuck
from poop.hfdp.adapter.ducks.turkey import Turkey
from poop.hfdp.adapter.ducks.turkey_adapter import TurkeyAdapter
from poop.hfdp.adapter.ducks.wild_turkey import WildTurkey


def main() -> None:
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
