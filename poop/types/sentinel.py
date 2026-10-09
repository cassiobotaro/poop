from typing import TYPE_CHECKING

from poop.types._cloak import cloak
from poop.types._unwrap import _is_absent
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass
    from poop.types.string import Str


class Sentinel(Object):
    """Python 3.15's `sentinel` (PEP 661): a unique marker that prints as its name.

    What CPython answers, and so what this does: every `sentinel("MISSING")`
    is a *new* object — two calls with one name are not identical and do not
    compare equal — whose `repr` is the name, or the `repr` keyword when one
    is given; it is truthy, hashes by identity, and answers no message of its
    own beyond `Object`'s, so `x.is_identical(MISSING)` is the question it
    exists for. `copy` preserving identity and pickling by name are CPython's
    halves that POOP has no surface for; the `|` that builds a type union
    (`int | MISSING`) belongs to annotations, which POOP does not write, so
    `Sentinel` declines `|` like any other operand.
    """

    __slots__ = ("_name", "_repr")

    def __init__(self, name: Str, repr_: Str | NoneClass | None = None) -> None:
        self._name = name
        self._repr = name if _is_absent(repr_) else repr_

    def __str__(self) -> str:
        return str(self._repr)

    __repr__ = __str__


cloak(Sentinel, "sentinel")
