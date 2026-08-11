from __future__ import annotations

import builtins as _builtins
from abc import abstractmethod
from collections import deque
from collections.abc import Callable, Iterator
from functools import reduce as functools_reduce
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.enumerate import Enumerate
    from poop.types.filter import Filter
    from poop.types.map import Map
    from poop.types.none import NoneClass
    from poop.types.object import Object
    from poop.types.zip import Zip

from poop.types._argument import MISSING
from poop.types._cloak import cloak
from poop.types._minmax import _MISSING, _minmax
from poop.types._mutated import iterating, reword_if_native
from poop.types._unwrap import _is_absent
from poop.types.boolean import false, to_boolean
from poop.types.int import Int
from poop.types.none import none


def _sorted(
    iterable: Any,
    key: Callable[[Any], Any] | NoneClass | None,
    reverse: Any,
    selector: str = "sorted",
) -> Any:
    """Assemble the optional `key` kwarg and call `sorted`.

    Shared by List (`sorted` and the in-place `sort`) and Tuple, which each
    answer their own type and so cannot inherit a single message. Passing
    `key=None` explicitly would work at runtime but matches no `sorted`
    overload, so the kwarg is omitted when there is no key.

    Absent is `_is_absent`, the same test every other optional argument in the
    language uses: POOP's `None` is a `NoneClass` instance, so `is None` let it
    through as a comparison block and `xs.sorted(key=None)` answered
    `'NoneType' object is not callable`.
    """
    from poop.types._argument import a_key

    kwargs: dict[str, Any] = {"reverse": bool(reverse)}
    if not _is_absent(key):
        # The one place every `sorted`/`sort` key passes through, as `_minmax`
        # is for `min`/`max`. A non-block reached CPython's sort and answered
        # `'int' object is not callable`.
        kwargs["key"] = a_key(key, selector)
    return _builtins.sorted(iterable, **kwargs)


class _IterableMixin:
    # An empty `__slots__`, because a slot-less class anywhere in an MRO
    # restores the per-instance `__dict__` for everything below it — this
    # mixin alone defeated the declaration on 36 of the 49 wrappers, so a
    # `Str` accepted attached state and two equal `Str`s could carry
    # different attributes. It cannot collide with a concrete class's own
    # slots, which is what makes it safe on all of them.
    __slots__ = ()

    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...

    def _iter_items(self) -> Iterator[Any]:
        return iter(self)

    def do(self, block: Callable[[Any], Any] = MISSING) -> NoneClass:
        from poop.types._argument import a_block

        block = a_block(block, "do")
        # The one place every collection's iteration is driven to exhaustion,
        # so it is where a mutation mid-iteration surfaces: CPython's
        # `dictionary changed size during iteration` names a `for` loop the
        # program did not write, and a word POOP does not use for a `dict`.
        try:
            deque(map(block, self._iter_items()), maxlen=0)
        except RuntimeError as exc:
            raise reword_if_native(exc, iterating(self)) from None
        return none

    def map(self, block: Callable[[Any], Any] = MISSING) -> Map:
        from poop.types._argument import a_block
        from poop.types.map import Map

        # Eagerly, though the view is lazy: this is the half no wording change
        # reaches. A `Map` built over a non-block simply fails later, somewhere
        # else entirely — or never, if the view is never walked.
        return Map(self, a_block(block, "map"))

    def filter(self, block: Callable[[Any], Any] = MISSING) -> Filter:
        from poop.types._argument import a_block
        from poop.types.filter import Filter

        return Filter(self, a_block(block, "filter"))

    def filter_false(self, block: Callable[[Any], Any] = MISSING) -> Filter:
        from poop.types._argument import a_block
        from poop.types.filter import Filter

        block = a_block(block, "filter_false")
        return Filter(self, lambda x: not bool(block(x)))

    def find(self, block: Callable[[Any], Any] = MISSING) -> Any:
        from poop.types._argument import a_block

        block = a_block(block, "find")
        for item in self._iter_items():
            if bool(block(item)):
                return item
        return none

    def reduce(
        self, init: Any = MISSING, block: Callable[[Any, Any], Any] = MISSING
    ) -> Any:
        from poop.types._argument import MISSING, a_block
        from poop.types.exceptions import MIRRORS

        if init is MISSING:
            # Named separately: `#reduce expects a block, got nothing` would be
            # true and unhelpful for `xs.reduce()`, where the initial value is
            # what is missing first.
            raise MIRRORS["TypeError"](
                "#reduce expects an initial value and a block, got nothing — "
                "write .reduce(start, lambda a, b: …)"
            )
        block = a_block(block, "reduce", param="a, b")
        return functools_reduce(block, self._iter_items(), init)

    def sum(self, start: Any = _MISSING) -> Any:
        items = self._iter_items()
        if start is not _MISSING:
            return functools_reduce(lambda a, b: a + b, items, start)
        try:
            first = next(items)
        except StopIteration:
            return Int(0)
        return functools_reduce(lambda a, b: a + b, items, first)

    def min(
        self,
        *,
        key: Callable[[Any], Any] | NoneClass | None = None,
        default: Any = _MISSING,
    ) -> Any:
        # Keyword-only, as CPython spells `min(iterable, *, key, default)` and
        # for the reason the scalar rungs settled: positionally a block is
        # indistinguishable from a value, and `xs.min(0)` — the plain reading
        # of "the smallest, or 0 if empty" — handed `0` to the key slot.
        return _minmax(_builtins.min, "#min", self._iter_items(), key, default)

    def max(
        self,
        *,
        key: Callable[[Any], Any] | NoneClass | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(_builtins.max, "#max", self._iter_items(), key, default)

    def sorted(
        self,
        *,
        key: Callable[[Any], Any] | NoneClass | None = None,
        reverse: Boolean = false,
    ) -> Any:
        # `no_sorted` forbids `sorted(col)` and names `col.sorted()`, and the
        # message existed on `List` and `Tuple` only — so `{2, 1}.sorted()`,
        # the ordinary way to look at an unordered collection in order, was
        # banned with nowhere to go. A `List`, as CPython's `sorted` always
        # answers a `list` whatever it was handed; `Tuple` overrides to keep
        # its own type, which can hold an order.
        from poop.types.list import List

        return List(*_sorted(self._iter_items(), key, reverse))

    def all(self, block: Callable[[Any], Any] = MISSING) -> Boolean:
        from poop.types._argument import a_block

        block = a_block(block, "all")
        return to_boolean(_builtins.all(bool(block(x)) for x in self._iter_items()))

    def any(self, block: Callable[[Any], Any] = MISSING) -> Boolean:
        from poop.types._argument import a_block

        block = a_block(block, "any")
        return to_boolean(_builtins.any(bool(block(x)) for x in self._iter_items()))

    def enumerate(self, start: Int | NoneClass | None = None) -> Enumerate:
        from poop.types.enumerate import Enumerate

        return Enumerate(self, start)

    def zip(self, *others: Object, strict: Boolean | NoneClass | None = None) -> Zip:
        from poop.types.zip import Zip

        return Zip(self, *others, strict=strict)


# Cloaked as `object`, the root's own spelling: these methods are inherited by
# many wrappers, so no single builtin name is true for all of them — and left
# alone CPython blamed `_IterableMixin` in every wrong-arity message, a private name
# `_reject_private` exists to keep out of user code.
cloak(_IterableMixin, "object")
