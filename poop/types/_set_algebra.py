import operator
from typing import TYPE_CHECKING, Self

from poop.types._argument import a_collection
from poop.types.boolean import to_boolean

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from collections.abc import Set as AbstractSet

    from poop.types.boolean import Boolean
    from poop.types.frozen_set import FrozenSet
    from poop.types.object import Object


def _elements(other: object, selector: str) -> Iterable[Object]:
    """A set *method* operand as a raw iterable of its elements.

    Unlike the set operators (``|``/``&``/``-``/``^``, which require two
    set-likes), CPython's set *methods* — ``union``/``intersection``/
    ``difference``/``isdisjoint``/... — accept any iterable, so
    ``{1}.union([2, 3])`` is valid. A non-iterable operand is refused by
    ``a_collection``, in the name of the message it was handed to.
    """
    return a_collection(other, selector)


def probed[T](obj: T) -> T | FrozenSet:
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
    set is found. Recognised the way `_other_set` recognises an operand, and
    narrowed to a mutable `set`: a `FrozenSet` is already hashable and is
    answered by itself.
    """
    raw = _other_set(obj)
    if isinstance(raw, set):
        # Function-local: `frozen_set` imports this module.
        # circular: frozen_set imports _set_algebra
        from poop.types.frozen_set import FrozenSet  # noqa: PLC0415

        return FrozenSet(*raw)
    return obj


def _other_set(other: object) -> AbstractSet[Object] | None:
    """Return the raw ``set``/``frozenset`` backing a set-like operand.

    Recognised as a ``_SetAlgebraMixin`` — the class both ``Set`` and
    ``FrozenSet`` inherit the operators from, defined below in this same
    module, so no import cycle is in play — rather than by the duck-typed
    marker it used to carry. Returns ``None`` for anything else.
    """
    if isinstance(other, _SetAlgebraMixin):
        return other._data
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

    __slots__ = ()  # empty, as `_Mixin` says every mixin's must be

    # What the operators read: `len` and the set algebra. Each concrete class
    # narrows the slot to its own builtin — `set[Object]`, `frozenset[Object]`.
    _data: AbstractSet[Object]

    def _rewrap(self, raw: Iterable[Object]) -> Self:
        """`raw`'s elements as the receiver's own builtin kind."""
        raise NotImplementedError

    def _algebra(
        self,
        other: object,
        op: Callable[[AbstractSet[Object], AbstractSet[Object]], AbstractSet[Object]],
    ) -> Self:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return self._rewrap(op(self._data, raw))

    def _compare(
        self,
        other: object,
        op: Callable[[AbstractSet[Object], AbstractSet[Object]], bool],
    ) -> Boolean:
        raw = _other_set(other)
        if raw is None:
            return NotImplemented
        return to_boolean(op(self._data, raw))

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
        return self._compare(other, operator.le)

    def __lt__(self, other: object) -> Boolean:
        return self._compare(other, operator.lt)

    def __ge__(self, other: object) -> Boolean:
        return self._compare(other, operator.ge)

    def __gt__(self, other: object) -> Boolean:
        return self._compare(other, operator.gt)
