from poop.hfdp.adapter.ducks.duck import Duck
from poop.hfdp.adapter.ducks.duck_adapter import DuckAdapter
from poop.hfdp.adapter.ducks.mallard_duck import MallardDuck
from poop.hfdp.adapter.ducks.turkey import Turkey


def main() -> None:
    duck: Duck = MallardDuck()
    duck_adapter: Turkey = DuckAdapter(duck)

    for _ in range(10):
        print("The Duckadapter says...")
        duck_adapter.gobble()
        duck_adapter.fly()
