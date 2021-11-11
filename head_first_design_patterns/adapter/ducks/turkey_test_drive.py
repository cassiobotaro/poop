from adapters import DuckAdapter
from ducks import Duck, MallardDuck
from turkeys import Turkey

# Note: Using variables of type defined by protocols instead of concrete types
duck: Duck = MallardDuck()
duck_adapter: Turkey = DuckAdapter(duck)

# note: A duck adapter communicates through the turkey interface
for _ in range(10):
    print("The Duckadapter says...")
    duck_adapter.gobble()
    duck_adapter.fly()
