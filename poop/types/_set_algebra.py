import operator
from typing import TYPE_CHECKING, Any, ClassVar, Self, cast

from poop.types._argument import a_collection
from poop.types.boolean import to_boolean

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

    from poop.types.boolean import Boolean
    from poop.types.object import Object


def _elements(other: object, selector: str) -> Iterable[Object]:
    """A set *method* operand as a raw iterable of its elements.

    Unlike the set operators (``|``/``&``/``-``/``^``, which require two
    set-likes), CPython's set *methods* — ``union``/``intersection``/
    ``difference``/``isdisjoint``/... — accept any iterable, so
    ``{1}.union([2, 3])`` is valid. Every POOP collection is itself
    Python-iterable, so the cast states what the runtime already guarantees;
    a non-iterable operand is refused by ``a_collection``, in the name of the
    message it was handed to.
    """
    return cast("Iterable[Object]", a_collection(other, selector))


def probed(obj: Any) -> Any:
    """`obj` as something a set can be *asked* about.

    A `Set` is unhashable, so `s.includes({1})`, `s.discard({1})` and
    `s.remove({1})` all answered `cannot use 'set' as a set element` — a
    refusal about *storing*, for three messages that only look. CPython draws
    the line the other way: `set.__contains__`, `discard` and `remove` probe
    with a temporary `frozenset`, so `{1} in s` is an ordinary question with
    an ordinary answer (and `s.remove({1})` reaches its `KeyError`), while
    `s.add({1})` stays refused.

    The probe compares and hashes exactly as a stored `FrozenSet` does — both
    read the raw `frozenset` behind `_data` — so a set really held inside a
    set is found. Recognised through the `_set_like` marker `_other_set` uses,
    and narrowed to a mutable `set`: a `FrozenSet` is already hashable and is
    answered by itself.
    """
    raw = _other_set(obj)
    if isinstance(raw, set):
        # Function-local: `frozen_set` imports this module.
        # circular: frozen_set imports _set_algebra
        from poop.types.frozen_set import FrozenSet  # noqa: PLC0415

        return FrozenSet(*raw)
    return obj


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
    ``set``; ``frozenset({1}) | {2}`` is a ``frozenset``). Results are built
    through ``_rewrap`` so the receiver's builtin wins.

    The builtin's, not ``type(self)``: on a user subclass ``type(self)`` is the
    class built on the ``builtin_alias``, whose call *converts* its argument —
    so ``Bag() | {1}`` read ``Bag(1)`` as "convert ``1`` to a set" and answered
    ``cannot convert int to set``. CPython answers ``set`` from an operator on a
    ``set`` subclass, and so does POOP; ``_BytesLikeMixin._rewrap`` states the
    same rule for the bytes pair.

    The *messages* (``union``, ``isdisjoint``, ...) stay on each class rather
    than here: a wrong-arity call is reported under the function's
    ``__qualname__``, and a function shared by both classes can carry only one
    of ``set.isdisjoint`` and ``frozenset.isdisjoint``. The dunders below are
    never sent by name, so they are shared.
    """

    # An empty `__slots__`, because a slot-less class anywhere in an MRO
    # restores the per-instance `__dict__` for everything below it — see the
    # note in `_value_eq.py`.
    __slots__ = ()

    _set_like: ClassVar[bool] = True
    _data: Any

    def _rewrap(self, raw: Iterable[Object]) -> Self:
        """`raw`'s elements as the receiver's own builtin kind."""
        raise NotImplementedError

    def _algebra(self, other: object, op: Callable[[Any, Any], Any]) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return self._rewrap(op(self._data, raw))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return probed(item) in self._data

    def __and__(self, other: object) -> Self:
        return self._algebra(other, operator.and_)

    def __or__(self, other: object) -> Self:
        return self._algebra(other, operator.or_)

    def __sub__(self, other: object) -> Self:
        return self._algebra(other, operator.sub)

    def __xor__(self, other: object) -> Self:
        return self._algebra(other, operator.xor)

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
