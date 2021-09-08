from adapters import DuckAdapter
from ducks import Duck, MallardDuck
from turkeys import Turkey

duck: Duck = MallardDuck()
duck_adapter: Turkey = DuckAdapter(duck)

for _ in range(10):
    print("The Duckadapter says...")
    duck_adapter.gobble()
    duck_adapter.fly()
