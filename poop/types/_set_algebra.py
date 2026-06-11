from __future__ import annotations

from typing import Any, ClassVar, Self


def _other_set(other: object) -> Any:
    """Return the raw ``set``/``frozenset`` backing a set-like operand.

    Operands are recognised by the duck-typed ``_set_like`` marker rather than
    ``isinstance(other, Set | FrozenSet)``, which would create the
    Set <-> FrozenSet import cycle. Returns ``None`` for anything else.
    """
    if getattr(other, "_set_like", False):
        return other._data  # ty: ignore[unresolved-attribute]
    return None


class _SetAlgebraMixin:
    """Shared ``&``/``|``/``-``/``^`` operators for ``Set`` and ``FrozenSet``.

    CPython lets ``set`` and ``frozenset`` mix freely under these operators, and
    the result takes the *left* operand's type (``{1} | frozenset({2})`` is a
    ``set``; ``frozenset({1}) | {2}`` is a ``frozenset``). Results are built with
    ``type(self)`` so the receiver's class wins.
    """

    _set_like: ClassVar[bool] = True
    _data: Any

    def __and__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return type(self)(*(self._data & raw))

    def __or__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return type(self)(*(self._data | raw))

    def __sub__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return type(self)(*(self._data - raw))

    def __xor__(self, other: object) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return type(self)(*(self._data ^ raw))
