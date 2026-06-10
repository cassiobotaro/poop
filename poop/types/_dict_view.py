from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.dict import Dict


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
            cls.__name__ = name
            cls.__module__ = "builtins"

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
