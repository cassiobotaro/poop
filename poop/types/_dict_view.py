from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, cast

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types.dict import Dict


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
    from poop.types.dict_items import DictItems
    from poop.types.dict_keys import DictKeys
    from poop.types.frozen_set import FrozenSet
    from poop.types.set import Set

    if isinstance(other, DictKeys | DictItems | Set | FrozenSet):
        return _elements(other)
    return None


class _DictView(_IterableMixin, Object):
    """Base for the live Dict views (keys / values / items).

    Mirrors the ``_iterator_base.py`` pattern: a shared skeleton plus a
    ``_repr_name`` ClassVar set via ``__init_subclass__(name=...)``.
    Subclasses declare ``__slots__ = ()`` and override the
    ``_repr_items()`` hook (the inner repr text differs per view), plus the
    iteration / set-algebra / comparison members that genuinely differ.
    Only the truly-identical skeleton lives here.
    """

    __slots__ = ("_dict",)
    __hash__ = None  # type: ignore[assignment]
    _repr_name: ClassVar[str] = "dict_view"

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            cls._repr_name = name
            # class_name() reads type(x).__name__ — answer the CPython name.
            cloak(cls, name)

    def __init__(self, dict_: Dict) -> None:
        self._dict: Dict = dict_

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
