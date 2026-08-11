from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar, Literal, cast

from poop.types._at import at_index, no_element_equal_to
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.memory_view_iterator import MemoryViewIterator
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types._index import Index
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.string import Str

_memoryview = memoryview  # alias to avoid shadowing by MemoryView class name


class MemoryView(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"
    # CPython compares memoryview equal by value to bytes/bytearray (and
    # other memoryviews): `memoryview(b"abc") == b"abc"` is True. Share the
    # "bytes" group so the same holds in POOP.
    _eq_group: ClassVar[str] = "bytes"

    def __init__(self, value: _memoryview | MemoryView) -> None:
        self._value = value._value if isinstance(value, MemoryView) else value

    def __hash__(self) -> int:
        # Mirror CPython: a memoryview is hashable iff it is read-only and of
        # byte format, and then hashes equal to the underlying bytes. Keeping
        # this in sync with the "bytes" eq group preserves the eq/hash
        # invariant against Bytes.
        return hash(self._value)

    def hash(self) -> Int:
        """`Object.hash`, with the one reason CPython words differently.

        The other unhashable receivers answer `unhashable type: 'list'`, which
        `cannot_be_hashed` rewords. A writable memoryview answers `cannot hash
        writable memoryview object` — a `ValueError`, not a `TypeError`, so that
        rewrite never sees it, and the only sentence in the language that says
        *object* where POOP says receiver. "Writable" is a buffer-protocol word
        that `INFECTIONS.md` keeps out deliberately, so the reason is given in
        terms of what the reader wrote instead.
        """
        from poop.types.exceptions import MIRRORS

        try:
            return super().hash()
        except ValueError:
            raise MIRRORS["TypeError"](
                "a memoryview over a bytearray cannot be hashed — "
                "the bytes behind it can still change"
            ) from None

    def len(self) -> Int:
        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Index) -> Int:
        return Int(at_index(self._value, index, self))

    def slice(
        self,
        start_or_slice: Index | Slice | NoneClass | None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> MemoryView:
        # `mv[0:2]` is a `memoryview` in CPython and `no_subscript` names
        # `.slice(...)` as the substitute — every other sequence answered it.
        from poop.types.slice import _resolve_py_slice

        return MemoryView(self._value[_resolve_py_slice(start_or_slice, stop, step)])

    def includes(self, byte: Int) -> Boolean:
        # `98 in memoryview(b"ab")` is True in CPython and `no_in` names
        # `col.includes(x)`. Unwrapped through `_faithful`, as `Bytes.includes`
        # is, so a foreign argument reaches CPython whole rather than leaking
        # the internal `_value` name through dispatch.
        from poop.types._unwrap import _faithful

        operand: Any = _faithful(byte)
        return to_boolean(operand in self._value)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Int):
            return item._value in self._value
        return False

    def count(self, byte: Int) -> Int:
        # One argument, as CPython's `memoryview.count` takes — unlike the
        # text wrappers', which carry `start`/`end`.
        from poop.types._unwrap import _faithful

        operand: Any = _faithful(byte)
        return Int(self._value.count(operand))

    def index(
        self,
        byte: Int,
        start: Int | NoneClass | None = None,
        stop: Index | NoneClass | None = None,
    ) -> Int:
        # `includes` is the substitute `no_in` names, and this receiver was the
        # one sequence in the family that could be told an element is there and
        # not asked where — `List`, `Tuple`, `Range`, `Bytes` and `ByteArray`
        # all answer both. The failure routes through `no_element_equal_to` for
        # the reason it exists: CPython says `memoryview.index(x): x not found`,
        # the message written as a call with a placeholder where the value the
        # reader passed belongs.
        from poop.types._argument import _opt_stop, a_bound
        from poop.types._unwrap import _faithful

        operand: Any = _faithful(byte)
        try:
            return Int(
                self._value.index(
                    operand,
                    a_bound(start, "index", "start") or 0,
                    _opt_stop(a_bound(stop, "index", "stop"), len(self._value)),
                )
            )
        except ValueError:
            raise no_element_equal_to(self, byte) from None

    def hex(
        self,
        sep: Str | Bytes | NoneClass | None = None,
        bytes_per_sep: Int | NoneClass | None = None,
    ) -> Str:
        # The one message that shows the contents: `__str__` summarizes, and
        # `tobytes` copies the whole buffer to show any of it.
        from poop.types._unwrap import _faithful, _is_absent, _opt_int
        from poop.types.string import Str

        if _is_absent(sep):
            return Str(self._value.hex())
        return Str(self._value.hex(_faithful(sep), _opt_int(bytes_per_sep, 1)))

    def __iter__(self) -> Iterator[Int]:
        return (Int(b) for b in self._value)

    def iter(self) -> MemoryViewIterator:
        return MemoryViewIterator(self)

    def reversed(self) -> MemoryView:
        # `reversed(memoryview(b"ab"))` works in CPython, so `no_reversed`
        # bans a construct this receiver had no substitute for. A `MemoryView`
        # rather than an iterator of `Int`s: every receiver answers its own
        # kind, and the reversed native view is O(1) — it copies nothing.
        return MemoryView(self._value[::-1])

    def tobytes(self, order: Str | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        return Bytes(
            self._value.tobytes(cast(Literal["C", "F", "A"], _unwrap(order, "C")))
        )

    def __str__(self) -> str:
        # CPython prints `<memory at 0x70cb7ab59240>`: the raw pointer
        # `Object.__hash__` refuses to answer, under a class name (`memory`)
        # that is neither the POOP name nor the cloak — and unstable across
        # runs, so no test could pin it and no example could show it. Printing
        # the bytes themselves would re-materialize an arbitrarily large
        # buffer just to print it, which is the cost proposal 10 refused, so
        # this summarizes and `hex()` shows the contents on request.
        return f"<memoryview of {self._value.nbytes} bytes>"

    __repr__ = __str__


cloak(MemoryView, "memoryview")
