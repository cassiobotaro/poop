"""Notes:
- Duck is a protocol with methods: quack() and fly().
- MallardDuck is an implementation of Duck.
- Don't need to inherit from Duck, because of structural subtyping.
"""
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
