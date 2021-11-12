from random import Random


class DuckAdapter:
    def __init__(self, duck) -> None:
        self.duck = duck
        self.rand = Random()

    def gobble(self) -> None:
        self.duck.quack()

    def fly(self) -> None:
        if self.rand.randint(1, 6) == 0:
            self.duck.fly()
