"""Notes:
- DuckAdapter is a class that implements the Turkey interface.
- DuckAdapter adapts a Duck to beheave like a Turkey.
- TurkeyAdapter is a class that implements the Duck interface.
- TurkeyAdapter adapts a Turkey to beheave like a Duck.
- Don't have inheritance because of structural subtyping.
"""
from random import randint

from ducks import Duck
from turkeys import Turkey


class DuckAdapter:
    def __init__(self, duck: Duck):
        self.duck = duck

    def gobble(self) -> None:
        self.duck.quack()

    def fly(self) -> None:
        if randint(0, 5) == 0:
            self.duck.fly()


class TurkeyAdapter:
    def __init__(self, turkey: Turkey):
        self.turkey = turkey

    def quack(self) -> None:
        self.turkey.gobble()

    def fly(self) -> None:
        for _ in range(5):
            self.turkey.fly()
