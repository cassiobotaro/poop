"""Notes:
- Turkey is a protocol with methods: gobble() and fly().
- WildTurkey is an implementation of Turkey.
- Don't need to inherit from Turkey, because of structural subtyping.
"""
from typing import Protocol


class Turkey(Protocol):
    def gobble(self) -> None:
        ...

    def fly(self) -> None:
        ...


class WildTurkey:
    def gobble(self) -> None:
        print("Gobble gobble")

    def fly(self) -> None:
        print("I'm flying a short distance")
