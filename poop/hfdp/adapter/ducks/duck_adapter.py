from random import Random

from poop.hfdp.adapter.ducks.duck import Duck


class DuckAdapter:
    def __init__(self, duck: Duck) -> None:
        self.__duck = duck
        self.__rand = Random()

    def gobble(self) -> None:
        self.__duck.quack()

    def fly(self) -> None:
        if self.__rand.randint(1, 6) == 0:
            self.__duck.fly()
