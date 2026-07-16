"""Operand coercion shared by the numeric tower's ordering and equality.

``bool`` is an ``int`` subclass in CPython, so a POOP ``Boolean`` must compare
as ``1``/``0`` against ``Int``/``Float`` (``True > 0.5`` is ``True``,
``True == 1`` is ``True``). ``_num_value`` returns the raw Python number behind
any numeric-tower operand (``Int``, ``Float`` or ``Boolean``), or the
``_NOT_NUMERIC`` sentinel for a foreign operand — the caller then answers
``NotImplemented`` (ordering) or a plain ``false``/``true`` (equality), so a
mismatch raises CPython's faithful ``TypeError`` instead of leaking an
``AttributeError`` from a missing ``other._value``.
"""

import operator
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poop.types.boolean import Boolean

_NOT_NUMERIC: Any = object()


def _num_value(other: object) -> Any:
    from poop.types.boolean import Boolean
    from poop.types.float import Float
    from poop.types.int import Int

    if isinstance(other, Int | Float):
        return other._value
    if isinstance(other, Boolean):
        return 1 if other else 0
    return _NOT_NUMERIC


class _NumericCompareMixin:
    """The comparison protocol shared by the whole numeric tower.

    ``Int``, ``Float`` and ``Boolean`` order and compare identically once each
    supplies the raw Python number behind ``self`` via ``_order_value``: ``Int``
    and ``Float`` return ``self._value`` (the default), ``Boolean`` folds to
    ``1``/``0`` (``bool`` is an ``int`` subclass). ``Complex`` joins only the
    equality side of the tower — ``1 == (1+0j)`` is ``True`` — so ``__eq__`` /
    ``__ne__`` special-case it before consulting ``_num_value``. A foreign
    operand yields ``NotImplemented`` (ordering) or a plain ``false``/``true``
    (equality) for CPython's faithful ``TypeError`` / result.
    """

    __slots__ = ()
    _value: Any  # provided by Int/Float slots; Boolean overrides _order_value

    def _order_value(self) -> Any:
        return self._value

    def _order(self, other: object, op: Callable[[Any, Any], bool]) -> Boolean:
        from poop.types.boolean import to_boolean

        v = _num_value(other)
        if v is _NOT_NUMERIC:
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
        from poop.types.boolean import false, to_boolean
        from poop.types.complex import Complex

        if isinstance(other, Complex):
            return to_boolean(self._order_value() == other._value)
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return false
        return to_boolean(self._order_value() == v)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true
        from poop.types.complex import Complex

        if isinstance(other, Complex):
            return false if self._order_value() == other._value else true
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return true
        return false if self._order_value() == v else true
