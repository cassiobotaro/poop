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

from typing import Any

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
