"""`<`, `<=`, `>` and `>=` for the wrappers that order by their payload.

`Str`, `Bytes`, `ByteArray`, `List` and `Tuple` each wrote the four out in full,
and the four differed by one character. The duplication cost more than lines:
ordering `bytes` against `bytearray` — which CPython allows in both directions,
like `==` and `+` — had to be fixed in two classes, four methods each.

The payload is the one `_ValueEqMixin` already compares (`_eq_attr`). The
comparable set is narrower than equality's, though, so it is its own group:
`memoryview` compares *equal* to `bytes` by value and does not order against
anything, in CPython as here.
"""

import operator
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._cloak import cloak
from poop.types.boolean import to_boolean

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class _OrderedMixin:
    # Empty, for the reason `_ValueEqMixin` gives: one slot-less class in an
    # MRO restores the per-instance `__dict__` for everything below it.
    __slots__ = ()

    _eq_attr: ClassVar[str]
    # Wrappers sharing a non-None group order against each other, as `bytes`
    # and `bytearray` do. Anything else is a foreign operand: the comparison
    # answers `NotImplemented` and CPython raises the refusal POOP rewords.
    _order_group: ClassVar[str | None] = None

    def _ordered_with(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return True
        group = self._order_group
        return group is not None and group == getattr(other, "_order_group", None)

    def _compare(self, other: object, op: Callable[[Any, Any], bool]) -> Boolean:
        if not self._ordered_with(other):
            return NotImplemented
        attr = self._eq_attr
        return to_boolean(op(getattr(self, attr), getattr(other, attr)))

    def __lt__(self, other: object) -> Boolean:
        return self._compare(other, operator.lt)

    def __le__(self, other: object) -> Boolean:
        return self._compare(other, operator.le)

    def __gt__(self, other: object) -> Boolean:
        return self._compare(other, operator.gt)

    def __ge__(self, other: object) -> Boolean:
        return self._compare(other, operator.ge)


# Cloaked as `object`, like the other shared mixins: no single builtin name is
# true for every wrapper that inherits these.
cloak(_OrderedMixin, "object")
