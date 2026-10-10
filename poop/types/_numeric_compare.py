"""Operand coercion shared by the numeric tower's ordering and equality.

``bool`` is an ``int`` subclass in CPython, so a POOP ``Boolean`` must compare
as ``1``/``0`` against ``Int``/``Float`` (``True > 0.5`` is ``True``,
``True == 1`` is ``True``). ``_num_value`` returns the raw Python number behind
any numeric-tower operand (``Int``, ``Float`` or ``Boolean``), or the
``NOT_NUMERIC`` sentinel for a foreign operand — the caller then answers
``NotImplemented`` (ordering) or a plain ``false``/``true`` (equality), so a
mismatch raises CPython's faithful ``TypeError`` instead of leaking an
``AttributeError`` from a missing ``other._value``.
"""

import operator
from typing import TYPE_CHECKING

from poop.types._mixin import _Mixin
from poop.types._sentinel import NOT_NUMERIC, NotNumeric

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean


def _num_value(other: object) -> int | float | NotNumeric:
    # circular: boolean imports _numeric_compare
    from poop.types.boolean import Boolean  # noqa: PLC0415

    # circular: float imports _numeric_compare
    from poop.types.float import Float  # noqa: PLC0415

    # circular: int imports _numeric_compare
    from poop.types.int import Int  # noqa: PLC0415

    if isinstance(other, (Int, Float)):
        return other._value
    if isinstance(other, Boolean):
        return 1 if other else 0
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
        # circular: boolean imports _numeric_compare
        from poop.types.boolean import to_boolean  # noqa: PLC0415

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
        # circular: boolean imports _numeric_compare
        from poop.types.boolean import false, to_boolean  # noqa: PLC0415

        # circular: complex -> boolean -> _numeric_compare
        from poop.types.complex import Complex  # noqa: PLC0415

        if isinstance(other, Complex):
            return to_boolean(self._order_value() == other._value)
        v = _num_value(other)
        if v is NOT_NUMERIC:
            return false
        return to_boolean(self._order_value() == v)
