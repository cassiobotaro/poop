import builtins
from abc import abstractmethod
from collections import deque
from functools import reduce as functools_reduce
from typing import TYPE_CHECKING, Any, overload

from poop.types import mirrors
from poop.types._argument import Key, a_block, a_key
from poop.types._mixin import _Mixin

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

    from poop.types.boolean import Boolean
    from poop.types.enumerate import Enumerate
    from poop.types.filter import Filter
    from poop.types.list import List
    from poop.types.map import Map
    from poop.types.none import NoneClass
    from poop.types.object import Object
    from poop.types.zip import Zip

from poop.types._minmax import _minmax
from poop.types._mutated import iterating, reword_if_native
from poop.types._sentinel import MISSING, Missing
from poop.types._unwrap import _is_absent
from poop.types.boolean import false, to_boolean
from poop.types.int import Int
from poop.types.none import none


def _sorted[T](
    iterable: Iterable[T],
    key: Key[T],
    reverse: object,
    selector: str = "sorted",
) -> list[T]:
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
    # Gradual on purpose: typeshed's key-less `sorted` demands elements it can
    # prove comparable, and POOP's are compared when the sort runs — a
    # refusal there is reworded by `poop_message`, not ruled out here.
    kwargs: dict[str, Any] = {"reverse": bool(reverse)}
    if not _is_absent(key):
        # The one place every `sorted`/`sort` key passes through, as `_minmax`
        # is for `min`/`max`. A non-block reached CPython's sort and answered
        # `'int' object is not callable`.
        kwargs["key"] = a_key(key, selector)
    return builtins.sorted(iterable, **kwargs)


class _IterableMixin[T: Object](_Mixin):
    """The collection protocol, generic over the element it yields.

    Each concrete receiver names its element — `Str` yields `Str`, `Bytes`
    and `Range` yield `Int`, the sequences, sets and mappings yield `Object`
    — so a block parameter is a function over that element and `find`
    answers one of them, rather than a function from nothing to nothing.
    """

    __slots__ = ()  # empty, as `_Mixin` says every mixin's must be

    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...

    def _iter_items(self) -> Iterator[T]:
        return iter(self)

    def do(self, block: Callable[[T], object] | Missing = MISSING) -> NoneClass:
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

    def map[R: Object](self, block: Callable[[T], R] | Missing = MISSING) -> Map[T, R]:
        # circular: map imports _iterable_mixin
        from poop.types.map import Map  # noqa: PLC0415

        # Eagerly, though the view is lazy: this is the half no wording change
        # reaches. A `Map` built over a non-block simply fails later, somewhere
        # else entirely — or never, if the view is never walked.
        return Map(self, a_block(block, "map"))

    def filter(self, block: Callable[[T], object] | Missing = MISSING) -> Filter[T]:
        # circular: filter imports _iterable_mixin
        from poop.types.filter import Filter  # noqa: PLC0415

        return Filter(self, a_block(block, "filter"))

    def filter_false(
        self, block: Callable[[T], object] | Missing = MISSING
    ) -> Filter[T]:
        # circular: filter imports _iterable_mixin
        from poop.types.filter import Filter  # noqa: PLC0415

        block = a_block(block, "filter_false")
        return Filter(self, lambda x: not bool(block(x)))

    def find(self, block: Callable[[T], object] | Missing = MISSING) -> T | NoneClass:
        block = a_block(block, "find")
        return next((item for item in self._iter_items() if block(item)), none)

    def reduce[R](
        self,
        init: R | Missing = MISSING,
        block: Callable[[R, T], R] | Missing = MISSING,
    ) -> R:
        if init is MISSING:
            # Named separately: `#reduce expects a block, got nothing` would be
            # true and unhelpful for `xs.reduce()`, where the initial value is
            # what is missing first.
            raise mirrors.TypeError(
                "#reduce expects an initial value and a block, got nothing — "
                "write .reduce(start, lambda a, b: …)"
            )
        block = a_block(block, "reduce", param="a, b")
        return functools_reduce(block, self._iter_items(), init)

    def sum(self, start: Object | Missing = MISSING) -> Object:
        items = self._iter_items()
        # The first element, not `Int(0)`, when there is one: a collection
        # of `Str`s or `List`s sums without a start that matches its kind.
        # Gradual on purpose, as `_sorted`'s kwargs are: the running total is
        # whatever the elements' own `+` answers — an `Int` beside a `Float`
        # is a `Float` — and `Object` declares no `+` for a checker to
        # follow, so the sum is added up the way `builtins.sum` adds.
        total: Any = next(items, Int(0)) if start is MISSING else start
        for item in items:
            total = total + item
        return total

    # `min` and `max` are each an overload pair: without a default they
    # answer an element, with one they answer an element or it. One
    # signature saying `default: D | Missing = MISSING` answers `T | D` for
    # both, and ty leaves `D` unsolved when nothing was passed.
    @overload
    def min(self, *, key: Key[T] = None) -> T: ...
    @overload
    def min[D](self, *, key: Key[T] = None, default: D) -> T | D: ...
    def min[D](self, *, key: Key[T] = None, default: D | Missing = MISSING) -> T | D:
        # Keyword-only, as CPython spells `min(iterable, *, key, default)` and
        # for the reason the scalar rungs settled: positionally a block is
        # indistinguishable from a value, and `xs.min(0)` — the plain reading
        # of "the smallest, or 0 if empty" — handed `0` to the key slot.
        return _minmax(builtins.min, "#min", self._iter_items(), key, default)

    @overload
    def max(self, *, key: Key[T] = None) -> T: ...
    @overload
    def max[D](self, *, key: Key[T] = None, default: D) -> T | D: ...
    def max[D](self, *, key: Key[T] = None, default: D | Missing = MISSING) -> T | D:
        return _minmax(builtins.max, "#max", self._iter_items(), key, default)

    def sorted(self, *, key: Key[T] = None, reverse: Boolean = false) -> List:
        # `no_sorted` forbids `sorted(col)` and names `col.sorted()`, and the
        # message existed on `List` and `Tuple` only — so `{2, 1}.sorted()`,
        # the ordinary way to look at an unordered collection in order, was
        # banned with nowhere to go. A `List`, as CPython's `sorted` always
        # answers a `list` whatever it was handed; `Tuple` overrides to keep
        # its own type, which can hold an order.
        # circular: list imports _iterable_mixin
        from poop.types.list import List  # noqa: PLC0415

        return List(*_sorted(self._iter_items(), key, reverse))

    def all(self, block: Callable[[T], object] | Missing = MISSING) -> Boolean:
        return to_boolean(builtins.all(map(a_block(block, "all"), self._iter_items())))

    def any(self, block: Callable[[T], object] | Missing = MISSING) -> Boolean:
        return to_boolean(builtins.any(map(a_block(block, "any"), self._iter_items())))

    def enumerate(self, start: Int | NoneClass | None = None) -> Enumerate:
        # circular: enumerate imports _iterable_mixin
        from poop.types.enumerate import Enumerate  # noqa: PLC0415

        return Enumerate(self, start)

    def zip(self, *others: Object, strict: Boolean | NoneClass | None = None) -> Zip:
        # circular: zip imports _iterable_mixin
        from poop.types.zip import Zip  # noqa: PLC0415

        return Zip(self, *others, strict=strict)
