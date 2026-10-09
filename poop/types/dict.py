from reprlib import recursive_repr
from typing import TYPE_CHECKING, Self, cast, overload

from poop.types._argument import a_collection, a_pair
from poop.types._at import no_key, nothing_to_remove
from poop.types._cloak import cloak
from poop.types._mapping import _MappingMixin
from poop.types._sentinel import MISSING, Missing
from poop.types._unwrap import _is_absent
from poop.types.mapping_proxy import MappingProxy
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types.none import NoneClass
    from poop.types.object import Object


class Dict(_MappingMixin):
    """The mutable mapping: `_MappingMixin`'s read side plus the writes."""

    __slots__ = ("_data",)
    __hash__ = None

    def __init__(self) -> None:
        self._data: dict[Object, Object] = {}

    def at_put(self, key: Object, val: Object) -> Dict:
        self._data[key] = val
        return self

    def clear(self) -> NoneClass:
        self._data.clear()
        return none

    def copy(self) -> Dict:
        return Dict._wrapping(self._data.copy())

    def __or__(self, other: object) -> Dict:
        # `dict | frozendict` is a dict in CPython: the left operand's kind.
        if not isinstance(other, _MappingMixin):
            return NotImplemented
        return Dict._wrapping(self._data | other._data)

    def __ior__(self, other: object) -> Self:
        # CPython's ``d |= proxy`` updates in place — ``dict.__ior__`` is
        # ``dict.update``, which takes any mapping. A MappingProxy is not a
        # Dict, so returning NotImplemented would hand the operation to
        # MappingProxy's reflected ``__ror__``, rebind the name to a fresh
        # Dict, and silently leave any alias pointing at the unchanged
        # original. Unwrap the proxy here, as ``__eq__`` already does.
        if isinstance(other, MappingProxy):
            self._data.update(other._dict._data)
            return self
        if not isinstance(other, _MappingMixin):
            return NotImplemented
        self._data.update(other._data)
        return self

    @overload
    def pop(self, key: Object) -> Object: ...
    @overload
    def pop[D](self, key: Object, default: D) -> Object | D: ...
    def pop[D](self, key: Object, default: D | Missing = MISSING) -> Object | D:
        if default is MISSING:
            # Only the asserting form can fail: `pop(key, default)` answers the
            # default instead, which is why it is left to CPython.
            try:
                return self._data.pop(key)
            except KeyError:
                raise no_key(self, key) from None
        return self._data.pop(key, default)

    def popitem(self) -> Tuple:
        try:
            k, v = self._data.popitem()
        except KeyError:
            raise nothing_to_remove(self) from None
        return Tuple(k, v)

    def setdefault(self, key: Object, default: Object = none) -> Object:
        # CPython defaults the fill value to None — `d.setdefault(k)` returns
        # `none` and stores `k: none`, as `get` defaults to `none`.
        return self._data.setdefault(key, default)

    def update(
        self, other: Object | NoneClass | None = None, **pairs: Object
    ) -> NoneClass:
        # CPython's dict.update accepts a mapping (Dict / FrozenDict /
        # read-only MappingProxy) or an iterable of key/value pairs, e.g.
        # ``d.update([(k1, v1), (k2, v2)])`` — not just another dict.
        #
        # Both halves of `dict.update([E], **F)` are optional there, and this
        # mirrored neither: `d.update()` — a no-op in CPython — answered
        # `missing 1 required positional argument`, and `d.update(b=2)` an
        # `unexpected keyword argument`, though the *constructor* one line of
        # POOP away takes exactly that (`dict(b=2)`). One signature, two
        # answers, decided by which spelling the reader reached for. An absent
        # mapping is `_is_absent`, the test every other optional argument in
        # the language uses.
        if isinstance(other, _MappingMixin):
            self._data.update(other._data)
        elif isinstance(other, MappingProxy):
            self._data.update(other._dict._data)
        elif not _is_absent(other):
            # Each pair is a POOP Tuple — itself a 2-element iterable, so
            # dict.update unpacks it and raises the faithful ValueError on a
            # wrong-length element.
            # The cast stays: `a_pair` answers a collection, and only
            # unpacking it would prove the length — which is what `dict.update`
            # does next, with CPython's own `length 3; 2 is required` sentence
            # for a pair that is not one.
            self._data.update(
                cast(
                    "Iterable[tuple[Object, Object]]",
                    (a_pair(p, "update") for p in a_collection(other, "update")),
                )
            )
        # After the mapping, as CPython applies them: a name given both ways
        # wins as a keyword. The keys arrive as raw `str` — CPython's `**`
        # demands them — and are stored as `Str`, the key a `{"b": 2}` literal
        # would have written.
        for name, value in pairs.items():
            self._data[Str(name)] = value
        return none

    # A dict can hold itself as a value — the same cycle `List` guards against,
    # and the same ellipsis CPython prints for it. See the note on `List`.
    @recursive_repr(fillvalue="{...}")
    def __str__(self) -> str:
        return "{" + self._pairs() + "}"

    __repr__ = __str__


cloak(Dict, "dict")
