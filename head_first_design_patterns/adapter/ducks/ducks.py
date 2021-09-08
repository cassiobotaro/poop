from typing import Protocol


class Duck(Protocol):
    def quack(self) -> None:
        ...

    def fly(self) -> None:
        ...


class MallardDuck:
    def quack(self) -> None:
        print("Quack")

    def fly(self) -> None:
        print("I'm flying")
