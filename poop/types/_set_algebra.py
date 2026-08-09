from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Self, cast

from poop.types.boolean import to_boolean

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types.boolean import Boolean
    from poop.types.object import Object


def _elements(other: object) -> Iterable[Object]:
    """A set *method* operand as a raw iterable of its elements.

    Unlike the set operators (``|``/``&``/``-``/``^``, which require two
    set-likes), CPython's set *methods* — ``union``/``intersection``/
    ``difference``/``isdisjoint``/... — accept any iterable, so
    ``{1}.union([2, 3])`` is valid. Every POOP collection is itself
    Python-iterable, so the cast states what the runtime already guarantees;
    a non-iterable operand raises the faithful ``TypeError`` from the set call
    (mirroring ``{1}.union(5)``).
    """
    return cast("Iterable[Object]", other)


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

    # An empty `__slots__`, because a slot-less class anywhere in an MRO
    # restores the per-instance `__dict__` for everything below it — see the
    # note in `_value_eq.py`.
    __slots__ = ()

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

    # Comparison operators are subset/superset tests for sets in CPython
    # (``<`` proper subset, ``<=`` subset, ``>`` proper superset, ``>=``
    # superset), and ``set`` and ``frozenset`` mix freely. Without these,
    # augmented comparison falls through to ``Object`` and raises ``TypeError``.
    # Equality (``==``/``!=``) stays with ``_ValueEqMixin``.
    def __le__(self, other: object) -> Boolean:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return to_boolean(self._data <= raw)

    def __lt__(self, other: object) -> Boolean:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return to_boolean(self._data < raw)

    def __ge__(self, other: object) -> Boolean:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return to_boolean(self._data >= raw)

    def __gt__(self, other: object) -> Boolean:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return to_boolean(self._data > raw)
