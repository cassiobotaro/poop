from collections.abc import Iterator
from operator import index as _index
from typing import TYPE_CHECKING

from poop.types._at import at_index
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._unwrap import _faithful
from poop.types.boolean import to_boolean
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.object import Object
from poop.types.range_iterator import RangeIterator

if TYPE_CHECKING:
    from poop.types._index import Index
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.none import NoneClass
    from poop.types.slice import Slice


class Range(_IterableMixin, Object):
    __slots__ = ("_start", "_stop", "_step")

    def __init__(
        self,
        start: Index,
        stop: Index,
        step: Index | NoneClass | None = None,
    ) -> None:
        from poop.types._unwrap import _is_absent

        # `_index` rather than `._value`: it takes the whole index rung of the
        # tower (`range(True, 5)` is `range(1, 5)` in CPython) and answers
        # CPython's own TypeError for anything else, where reading the slot
        # leaked `#_value`.
        resolved: Index
        if _is_absent(step):
            resolved = Int(1 if _index(start) <= _index(stop) else -1)
        else:
            resolved = step
        if _index(resolved) == 0:
            raise MIRRORS["ValueError"]("step must not be zero")
        # Normalized to Int, as CPython does: `range(True, 5).start` is `1`,
        # not `True`. (A `slice`, by contrast, keeps what it was given.)
        self._start = Int(_index(start))
        self._stop = Int(_index(stop))
        self._step: Int = Int(_index(resolved))

    def _range(self) -> range:
        start, stop, step = self._start._value, self._stop._value, self._step._value
        sign = 1 if step > 0 else -1
        return range(start, stop + sign, step)

    def _iter(self) -> Iterator[Int]:
        for i in self._range():
            yield Int(i)

    def __iter__(self) -> Iterator[Int]:
        return self._iter()

    def iter(self) -> RangeIterator:
        return RangeIterator(self)

    def slice(
        self,
        start_or_slice: Index | Slice | NoneClass | None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> Range:
        from poop.types.slice import _resolve_py_slice

        py = _resolve_py_slice(start_or_slice, stop, step)
        # A Range answers a Range, as `range(10)[1:3]` answers `range(1, 3)`
        # and as `reversed()` right below already does. Wrapping the selected
        # elements in a List instead allocated one Int per member of the
        # result: `range(1000000000000).slice(0, 3)` is three elements in
        # CPython and was a materialized trillion here.
        sliced = self._range()[py]
        # Round-trip the exclusive stop back through __init__'s inclusive
        # convention, exactly as `reversed()` does.
        sign = 1 if sliced.step > 0 else -1
        return Range(Int(sliced.start), Int(sliced.stop - sign), Int(sliced.step))

    def includes(self, item: Int) -> Boolean:
        # getattr-unwrap: a non-`_value` argument (List, Set, …) reaches
        # range.__contains__ raw, which answers False by equality scan (as in
        # Python), instead of leaking the internal `_value` name through dispatch.
        return to_boolean(_faithful(item) in self._range())

    def count(self, value: Int) -> Int:
        return Int(self._range().count(_faithful(value)))

    def index(self, value: Int) -> Int:
        return Int(self._range().index(_faithful(value)))

    def start(self) -> Int:
        return self._start

    def stop(self) -> Int:
        """The exclusive bound CPython answers — `range(3).stop` is `3`.

        Not the `_stop` slot. The inclusive upper bound is how a `Range` stores
        a sequence (`__eq__` calls it "an internal encoding" for the same
        reason), and `_range()` is the one place that encoding is undone.
        Answering the slot published it: `range(3).stop()` said `2`, while
        `Slice.stop()` — handed its bound rather than encoding one — said what
        Python says. One selector, two meanings, decided by the receiver.
        """
        return Int(self._range().stop)

    def step(self) -> Int:
        return self._step

    def at(self, index: Index) -> Int:
        return Int(at_index(self._range(), index, self))

    def reversed(self) -> Range:
        # Reverse the materialized forward sequence and re-encode it as a
        # POOP Range. POOP ranges use an inclusive upper bound (`_range`
        # adds `sign` to stop), so the forward sequence's last element is
        # not necessarily `_stop`: Range(0, 10, 3) yields [0, 3, 6, 9], so
        # seeding the reversed range from `_stop` (10) would produce the
        # non-members [10, 7, 4, 1]. Slice-reverse gives the correct,
        # empty-safe sequence; shift the resulting exclusive stop back by
        # `sign` to round-trip through __init__'s inclusive convention.
        reversed_range = self._range()[::-1]
        sign = 1 if reversed_range.step > 0 else -1
        return Range(
            Int(reversed_range.start),
            Int(reversed_range.stop - sign),
            Int(reversed_range.step),
        )

    def len(self) -> Int:
        return Int(len(self._range()))

    def __eq__(self, other: object) -> Boolean:
        # Mirror Python's `range` value equality: two ranges are equal when
        # they produce the same sequence. POOP's inclusive upper bound is an
        # internal encoding, so compare the materialized native ranges rather
        # than the raw `_start`/`_stop`/`_step` fields (e.g. Range(0, 4, 2)
        # and Range(0, 5, 2) both yield [0, 2, 4] and must compare equal).
        if isinstance(other, Range):
            return to_boolean(self._range() == other._range())
        return to_boolean(False)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self == other) else true

    def __hash__(self) -> int:
        # Equal ranges must hash equally; defer to the native range's hash,
        # which is consistent with its value-equality semantics.
        return hash(self._range())

    def __str__(self) -> str:
        # Through the materialized range, like `stop()`: printing the raw slots
        # showed `range(0, 2)` for `range(3)` — a spelling that, read back as
        # POOP source, is a *different* sequence. A displayed range has to be
        # the range it describes, and that is the exclusive form.
        native = self._range()
        if native.step == 1:
            return f"range({native.start}, {native.stop})"
        return f"range({native.start}, {native.stop}, {native.step})"

    __repr__ = __str__


cloak(Range, "range")
