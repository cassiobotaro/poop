"""Operand coercion shared by the numeric tower's ordering and equality.

``bool`` is an ``int`` subclass in CPython, so a POOP ``Boolean`` must compare
as ``1``/``0`` against ``Int``/``Float`` (``True > 0.5`` is ``True``,
``True == 1`` is ``True``). ``_num_value`` returns the raw Python number behind
any numeric-tower operand (``Int``, ``Float`` or ``Boolean``), or the
``NOT_NUMERIC`` sentinel for a foreign operand — the caller then answers
``NotImplemented`` (ordering) or a plain ``false``/``true`` (equality), so a
mismatch raises CPython's faithful ``TypeError`` instead of leaking an
``AttributeError`` from a missing ``other._value``.

``_num_value`` reads the number through the hook the mixin below declares,
``_order_value``, rather than importing the three rungs and testing them in
order: every rung inherits the mixin, so one ``isinstance`` on it is the whole
test. This runs on every comparison between numbers, and the three local
imports it used to make were a third of the cost; the two names it still
needs from ``boolean`` and ``complex`` are lazy imports, resolved on first use
and plain globals after that.
"""

import operator
from typing import TYPE_CHECKING

from poop.types._mixin import _Mixin
from poop.types._sentinel import NOT_NUMERIC, NotNumeric

# circular: boolean inherits this module's mixin, complex imports boolean
lazy from poop.types.boolean import false, to_boolean
lazy from poop.types.complex import Complex

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean


def _num_value(other: object) -> int | float | NotNumeric:
    if isinstance(other, _NumericCompareMixin):
        return other._order_value()
    return NOT_NUMERIC


class _NumericCompareMixin(_Mixin):  # noqa: PLW1641 — the numeric rungs hash themselves
    """The comparison protocol shared by the whole numeric tower.

    ``Int``, ``Float`` and ``Boolean`` order and compare identically once each
    supplies the raw Python number behind ``self`` via ``_order_value``: ``Int``
    and ``Float`` answer ``self._value``, ``Boolean`` folds to ``1``/``0``
    (``bool`` is an ``int`` subclass). The hook is the one thing the mixin
    needs, so it is the one thing it declares — a ``_value`` slot it does not
    have would be a phantom ``Boolean`` inherits without carrying. ``Complex`` joins only the
    equality side of the tower — ``1 == (1+0j)`` is ``True`` — so ``__eq__`` /
    ``__ne__`` special-case it before consulting ``_num_value``. A foreign
    operand yields ``NotImplemented`` (ordering) or a plain ``false``/``true``
    (equality) for CPython's faithful ``TypeError`` / result.
    """

    __slots__ = ()

    def _order_value(self) -> int | float:
        """The raw Python number behind ``self``. Supplied by each rung."""
        raise NotImplementedError

    def _order(
        self, other: object, op: Callable[[int | float, int | float], bool]
    ) -> Boolean:
        v = _num_value(other)
        if v is NOT_NUMERIC:
            return NotImplemented
        return to_boolean(op(self._order_value(), v))

    def __lt__(self, other: object) -> Boolean:
        return self._order(other, operator.lt)

    def __le__(self, other: object) -> Boolean:
        return self._order(other, operator.le)

    def __gt__(self, other: object) -> Boolean:
        return self._order(other, operator.gt)

    def __ge__(self, other: object) -> Boolean:
        return self._order(other, operator.ge)

    def __eq__(self, other: object) -> Boolean:
        v = _num_value(other)
        if v is NOT_NUMERIC:
            # The tower first, `Complex` only on the miss: `Int == Int` is the
            # common case and never needs the class this binds.
            if isinstance(other, Complex):
                return to_boolean(self._order_value() == other._value)
            return false
        return to_boolean(self._order_value() == v)
