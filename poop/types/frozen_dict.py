from reprlib import recursive_repr
from typing import TYPE_CHECKING, Self

from poop.types import mirrors
from poop.types._mapping import _MappingMixin
from poop.types._message import article
from poop.types.mapping_proxy import _mapping_data

if TYPE_CHECKING:
    from poop.types.object import Object


class FrozenDict(_MappingMixin, name="frozendict"):
    """Python 3.15's `frozendict` (PEP 814): `Dict`'s read side, and a hash.

    Not a `Dict` subclass, as `frozendict` is not a `dict` subclass —
    `fd.is_instance(dict)` is false — and not a `MappingProxy` either: a proxy
    is a live read-only *view* of a mapping that may change under it, and a
    `FrozenDict` is a *value*, which is why it can hash where the proxy cannot.
    Both exist in CPython; `fd.keys().mapping()` is a proxy over the frozen
    dict, as `frozendict().keys().mapping` is.

    Follows CPython on every edge: equality ignores insertion order (as every
    mapping's does) and holds across the kinds — `fd == {"a": 1}` both ways;
    `copy` answers the receiver itself, as `frozenset.copy` does; `|` with any
    mapping answers a `FrozenDict`, while `dict | frozendict` answers a `Dict`
    (the left operand's kind, as the set pair does — `Dict.__or__` claims every
    mapping, so CPython's `frozendict.__ror__` has no reachable twin here);
    and hashing a value that cannot be hashed is refused by `Object.hash`'s
    sentence.
    """

    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: dict[Object, Object] = {}

    def copy(self) -> Self:
        # CPython answers the receiver itself — a frozendict is immutable, so
        # copying it is pointless and ``fd.copy() is fd`` is True.
        return self

    def __hash__(self) -> int:
        # Order-blind, as equality is: two frozendicts that compare equal hash
        # alike whatever order their entries were given in. Each value is
        # hashed on its own rather than inside a `(key, value)` pair: a pair
        # fails inside the frozenset as `cannot use 'tuple' as a set element`,
        # naming a tuple the program never wrote, where `hash(value)` raises
        # CPython's own `unhashable type: 'list'` — the sentence `Object.hash`
        # and the error report reword.
        # Each value hashed by name here, not left to `Object.hash`'s
        # rewording: that one said the *value* "has no place as a set element
        # or a dict key", and a frozendict value is a legal place for a list.
        hashed = []
        for key, value in self._data.items():
            try:
                hashed.append((key, hash(value)))
            except TypeError:
                raise mirrors.TypeError(
                    f"frozendict cannot be hashed — it holds "
                    f"{article(type(value).__name__)}, which cannot be"
                ) from None
        return hash(frozenset(hashed))

    def __or__(self, other: object) -> FrozenDict:
        other_data = _mapping_data(other)
        if other_data is None:
            return NotImplemented
        return FrozenDict._wrapping(self._data | other_data)

    # A frozen dict cannot hold itself, but a `Dict` it holds can hold it —
    # the same cycle `Dict.__str__` guards against, one level further out.
    @recursive_repr(fillvalue="frozendict({...})")
    def __str__(self) -> str:
        if not self._data:
            return "frozendict()"
        return "frozendict({" + self._pairs() + "})"
