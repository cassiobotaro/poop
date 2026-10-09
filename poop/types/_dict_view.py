import operator
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, cast

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, to_boolean
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.object import Object
from poop.types.set import Set

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types._mapping import _MappingMixin
    from poop.types.boolean import Boolean


def _elements(other: object) -> set[Object]:
    """A set-algebra operand as a plain set of its elements.

    CPython's set-like views take *any iterable* for ``| & - ^`` and for
    ``isdisjoint`` — ``{"a": 1}.keys() | ["a", "c"]`` is valid — so the operand
    is only iterated, never asked for an internal slot. Every POOP collection
    is Python-iterable, so the cast states what the runtime already
    guarantees, and a non-iterable operand raises the faithful ``TypeError``
    from ``set(other)`` (``'int' object is not iterable``) — the same path
    ``_SetAlgebraMixin._elements`` documents for the set *method* forms.
    """
    return set(cast("Iterable[Object]", other))


def _operand(other: object) -> set[Object] | None:
    """``_elements(other)`` for a set *operator*, or ``None`` to decline.

    ``isdisjoint`` is a message and refuses a scalar through ``a_collection``.
    An operator handed one answers ``NotImplemented`` instead, so the refusal
    is the sentence every other operator in the language gives —
    ``dict_keys does not understand #| with an int`` — where ``set(5)``
    answered ``'int' object is not iterable``.
    """
    if isinstance(other, Iterable):
        return _elements(other)
    return None


def _set_like_elements(other: object) -> set[Object] | None:
    """``_elements(other)`` when the operand is set-like, else ``None``.

    The asymmetry CPython keeps: ``dict_keys <= list`` is a ``TypeError``
    though ``dict_keys | list`` is fine, so the comparison operators need the
    narrower question. Set-like means the two set-like views (``dict_values``
    is not one) or a ``Set`` / ``FrozenSet``.

    The imports are function-local because every one of those modules imports
    this one. They are deliberately not the duck-typed ``_set_like`` marker
    ``_SetAlgebraMixin`` uses: that marker makes ``_other_set`` claim the
    operand, and a ``Set``/``FrozenSet`` must instead answer ``NotImplemented``
    so the view's reflected operator runs — CPython's
    ``frozenset({1}) | {2: 3}.keys()`` is a ``set``, not a ``frozenset``.
    """
    # circular: dict_items imports _dict_view
    from poop.types.dict_items import DictItems  # noqa: PLC0415

    # circular: dict_keys imports _dict_view
    from poop.types.dict_keys import DictKeys  # noqa: PLC0415

    if isinstance(other, (DictKeys, DictItems, Set, FrozenSet)):
        return _elements(other)
    return None


class _DictView[T: Object](_IterableMixin[T], Object):
    """Base for the live Dict views (keys / values / items).

    Mirrors the ``_iterator_base.py`` pattern: a shared skeleton plus a
    ``_repr_name`` ClassVar set via ``__init_subclass__(name=...)``.
    Subclasses declare ``__slots__ = ()`` and override the
    ``_repr_items()`` hook (the inner repr text differs per view), plus the
    iteration / set-algebra / comparison members that genuinely differ.
    Only the truly-identical skeleton lives here.
    """

    __slots__ = ("_dict",)
    _repr_name: ClassVar[str] = "dict_view"

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            cls._repr_name = name
            # class_name() reads type(x).__name__ — answer the CPython name.
            cloak(cls, name)

    def __init__(self, dict_: _MappingMixin) -> None:
        self._dict: _MappingMixin = dict_

    def len(self) -> Int:
        return Int(len(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def mapping(self) -> MappingProxy:
        return MappingProxy(self._dict)

    def _repr_items(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self._repr_name}([{self._repr_items()}])"

    __repr__ = __str__


# Cloaked as `object`, the root's own spelling: these methods are inherited by
# many wrappers, so no single builtin name is true for all of them — and left
# alone CPython blamed `_DictView` in every wrong-arity message, a private name
# `_reject_private` exists to keep out of user code.
cloak(_DictView, "object")


class _SetLikeView[T: Object](_DictView[T]):
    """The set algebra and comparisons `dict_keys` and `dict_items` share.

    The two views differed only in what their own side is — the keys view
    itself, or a set of `Tuple` pairs — and spelled every operator twice over
    that difference. `_own` is that difference; everything else is written
    once. `isdisjoint` stays on each class: it is a message, and a wrong-arity
    report names the function's owner.
    """

    __slots__ = ()
    # Set-like and compared by contents, which change under it: unhashable,
    # as in CPython. `dict_values` is neither, and hashes by identity.
    __hash__ = None  # type: ignore[assignment]

    def _own(self) -> Any:
        """The receiver's own side, as something a `set` operator accepts."""
        raise NotImplementedError

    def _algebra(self, other: object, op: Callable[[Any, Any], Any]) -> Set:
        raw = _operand(other)
        if raw is None:
            return NotImplemented
        return Set(*op(self._own(), raw))

    def _reflected(self, other: object, op: Callable[[Any, Any], Any]) -> Set:
        raw = _operand(other)
        if raw is None:
            return NotImplemented
        return Set(*op(raw, self._own()))

    def _compare(self, other: object, op: Callable[[Any, Any], bool]) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(op(self._own(), raw))

    def __or__(self, other: object) -> Set:
        return self._algebra(other, operator.or_)

    def __ror__(self, other: object) -> Set:
        return self._reflected(other, operator.or_)

    def __and__(self, other: object) -> Set:
        return self._algebra(other, operator.and_)

    def __rand__(self, other: object) -> Set:
        return self._reflected(other, operator.and_)

    def __sub__(self, other: object) -> Set:
        return self._algebra(other, operator.sub)

    def __rsub__(self, other: object) -> Set:
        return self._reflected(other, operator.sub)

    def __xor__(self, other: object) -> Set:
        return self._algebra(other, operator.xor)

    def __rxor__(self, other: object) -> Set:
        return self._reflected(other, operator.xor)

    def __eq__(self, other: object) -> Boolean:
        # Equality answers false for a non-set-like operand rather than
        # raising, exactly as `dict.keys() == [...]` does in CPython.
        raw = _set_like_elements(other)
        if raw is None:
            return false
        return to_boolean(self._own() == raw)

    def __le__(self, other: object) -> Boolean:
        return self._compare(other, operator.le)

    def __lt__(self, other: object) -> Boolean:
        return self._compare(other, operator.lt)

    def __ge__(self, other: object) -> Boolean:
        return self._compare(other, operator.ge)

    def __gt__(self, other: object) -> Boolean:
        return self._compare(other, operator.gt)


cloak(_SetLikeView, "object")
