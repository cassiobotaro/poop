from head_first_design_patterns.adapter.ducks.duck import Duck
from head_first_design_patterns.adapter.ducks.duck_adapter import DuckAdapter
from head_first_design_patterns.adapter.ducks.mallard_duck import MallardDuck
from head_first_design_patterns.adapter.ducks.turkey import Turkey

duck: Duck = MallardDuck()
duck_adapter: Turkey = DuckAdapter(duck)

for _ in range(10):
    print("The Duckadapter says...")
    duck_adapter.gobble()
    duck_adapter.fly()
