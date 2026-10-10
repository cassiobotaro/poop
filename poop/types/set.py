import operator
from typing import TYPE_CHECKING, ClassVar, Self

from poop.types._at import no_element_equal_to, nothing_to_remove
from poop.types._iterable_mixin import _IterableMixin
from poop.types._set_algebra import (
    _elements,
    _other_set,
    _SetAlgebraMixin,
    probed,
)
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object
from poop.types.set_iterator import SetIterator

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from collections.abc import Set as AbstractSet

    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass


class Set(_SetAlgebraMixin, _ValueEqMixin, _IterableMixin[Object], Object, name="set"):
    __slots__ = ("_data",)
    _data: set[Object]
    _eq_attr: ClassVar[str] = "_data"
    _eq_group: ClassVar[str] = "set"
    __hash__ = None

    def __init__(self, *elements: Object) -> None:
        self._data: set[Object] = set(elements)

    def add(self, obj: Object) -> NoneClass:
        self._data.add(obj)
        return none

    def remove(self, obj: Object) -> NoneClass:
        # `discard` is the spelling that asks; `remove` asserts, so only this
        # one can fail. CPython answers the element's bare repr.
        try:
            self._data.remove(probed(obj))
        except KeyError:
            raise no_element_equal_to(self, obj, "KeyError") from None
        return none

    def discard(self, obj: Object) -> NoneClass:
        self._data.discard(probed(obj))
        return none

    def clear(self) -> NoneClass:
        self._data.clear()
        return none

    def copy(self) -> Set:
        return Set(*self._data)

    def pop(self) -> Object:
        try:
            return self._data.pop()
        except KeyError:
            raise nothing_to_remove(self) from None

    def union(self, *others: Object) -> Set:
        return Set(*self._data.union(*(_elements(o, "union") for o in others)))

    def intersection(self, *others: Object) -> Set:
        return Set(
            *self._data.intersection(*(_elements(o, "intersection") for o in others))
        )

    def difference(self, *others: Object) -> Set:
        return Set(
            *self._data.difference(*(_elements(o, "difference") for o in others))
        )

    def symmetric_difference(self, other: Object) -> Set:
        return Set(
            *self._data.symmetric_difference(_elements(other, "symmetric_difference"))
        )

    def update(self, *others: Object) -> NoneClass:
        self._data.update(*(_elements(o, "update") for o in others))
        return none

    def intersection_update(self, *others: Object) -> NoneClass:
        self._data.intersection_update(
            *(_elements(o, "intersection_update") for o in others)
        )
        return none

    def difference_update(self, *others: Object) -> NoneClass:
        self._data.difference_update(
            *(_elements(o, "difference_update") for o in others)
        )
        return none

    def symmetric_difference_update(self, other: Object) -> NoneClass:
        self._data.symmetric_difference_update(
            _elements(other, "symmetric_difference_update")
        )
        return none

    def isdisjoint(self, other: Object) -> Boolean:
        return to_boolean(self._data.isdisjoint(_elements(other, "isdisjoint")))

    def issubset(self, other: Object) -> Boolean:
        return to_boolean(self._data.issubset(_elements(other, "issubset")))

    def issuperset(self, other: Object) -> Boolean:
        return to_boolean(self._data.issuperset(_elements(other, "issuperset")))

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self)

    def len(self) -> Int:
        return Int(len(self._data))

    def _rewrap(self, raw: Iterable[Object]) -> Set:
        return Set(*raw)

    def iter(self) -> SetIterator:
        return SetIterator(self._data)

    def _inplace(
        self, other: object, op: Callable[[set[Object], AbstractSet[Object]], object]
    ) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        op(self._data, raw)
        return self

    # In-place set operators mutate the receiver (CPython ``s |= other`` keeps
    # ``s``'s identity, so aliases observe the change). Without these, augmented
    # assignment would fall back to the binary ``__or__``/... from
    # _SetAlgebraMixin, rebind the name to a fresh Set, and silently leave any
    # alias pointing at the unchanged original.
    def __ior__(self, other: object) -> Self:
        return self._inplace(other, operator.ior)

    def __iand__(self, other: object) -> Self:
        return self._inplace(other, operator.iand)

    def __isub__(self, other: object) -> Self:
        return self._inplace(other, operator.isub)

    def __ixor__(self, other: object) -> Self:
        return self._inplace(other, operator.ixor)

    def __str__(self) -> str:
        if not self._data:
            return "set()"
        return "{" + ", ".join(repr(item) for item in self._data) + "}"
