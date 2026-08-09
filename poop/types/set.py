from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar, Self

from poop.types._at import no_element_equal_to, nothing_to_remove
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._set_algebra import _elements, _other_set, _SetAlgebraMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object
from poop.types.set_iterator import SetIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.none import NoneClass

_set = set  # alias to avoid shadowing by Set class name in annotations


class Set(_SetAlgebraMixin, _ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_data",)
    _eq_attr: ClassVar[str] = "_data"
    _eq_group: ClassVar[str] = "set"
    __hash__ = None

    def __init__(self, *elements: Object) -> None:
        self._data: _set[Object] = _set(elements)

    def add(self, obj: Object) -> NoneClass:
        self._data.add(obj)
        return none

    def remove(self, obj: Object) -> NoneClass:
        # `discard` is the spelling that asks; `remove` asserts, so only this
        # one can fail. CPython answers the element's bare repr.
        try:
            self._data.remove(obj)
        except KeyError:
            raise no_element_equal_to(self, obj, "KeyError") from None
        return none

    def discard(self, obj: Object) -> NoneClass:
        self._data.discard(obj)
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
        return Set(*self._data.union(*(_elements(o) for o in others)))

    def intersection(self, *others: Object) -> Set:
        return Set(*self._data.intersection(*(_elements(o) for o in others)))

    def difference(self, *others: Object) -> Set:
        return Set(*self._data.difference(*(_elements(o) for o in others)))

    def symmetric_difference(self, other: Object) -> Set:
        return Set(*self._data.symmetric_difference(_elements(other)))

    def update(self, *others: Object) -> NoneClass:
        self._data.update(*(_elements(o) for o in others))
        return none

    def intersection_update(self, *others: Object) -> NoneClass:
        self._data.intersection_update(*(_elements(o) for o in others))
        return none

    def difference_update(self, *others: Object) -> NoneClass:
        self._data.difference_update(*(_elements(o) for o in others))
        return none

    def symmetric_difference_update(self, other: Object) -> NoneClass:
        self._data.symmetric_difference_update(_elements(other))
        return none

    def isdisjoint(self, other: Object) -> Boolean:
        return to_boolean(self._data.isdisjoint(_elements(other)))

    def issubset(self, other: Object) -> Boolean:
        return to_boolean(self._data.issubset(_elements(other)))

    def issuperset(self, other: Object) -> Boolean:
        return to_boolean(self._data.issuperset(_elements(other)))

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self._data)

    def len(self) -> Int:
        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def iter(self) -> SetIterator:
        return SetIterator(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    # In-place set operators mutate the receiver (CPython ``s |= other`` keeps
    # ``s``'s identity, so aliases observe the change). Without these, augmented
    # assignment would fall back to the binary ``__or__``/... from
    # _SetAlgebraMixin, rebind the name to a fresh Set, and silently leave any
    # alias pointing at the unchanged original.
    def __ior__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        self._data |= raw
        return self

    def __iand__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        self._data &= raw
        return self

    def __isub__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        self._data -= raw
        return self

    def __ixor__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        self._data ^= raw
        return self

    def __str__(self) -> str:
        if not self._data:
            return "set()"
        return "{" + ", ".join(repr(item) for item in self._data) + "}"

    __repr__ = __str__


cloak(Set, "set")
