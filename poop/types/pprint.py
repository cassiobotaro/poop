import pprint as _pprint
from typing import Any

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.string import Str


def _b(value: Boolean | None, default: bool) -> bool:
    return default if value is None else bool(value)


def _i(value: Int | None, default: int | None) -> int | None:
    if value is None:
        return default
    return value._value


class PrettyPrinter:
    """Reusable wrapper around Python's `pprint.PrettyPrinter`.

    Mirrors the underlying knobs (`indent`, `width`, `depth`,
    `compact`, `sort_dicts`, `underscore_numbers`). Defaults follow
    CPython exactly.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        indent: Int | None = None,
        width: Int | None = None,
        depth: Int | None = None,
        *,
        compact: Boolean | None = None,
        sort_dicts: Boolean | None = None,
        underscore_numbers: Boolean | None = None,
    ) -> None:
        self._impl = _pprint.PrettyPrinter(
            indent=_i(indent, 1) or 1,
            width=_i(width, 80) or 80,
            depth=_i(depth, None),
            compact=_b(compact, False),
            sort_dicts=_b(sort_dicts, True),
            underscore_numbers=_b(underscore_numbers, False),
        )

    def pprint(self, obj: Any) -> NoneClass:
        self._impl.pprint(obj)
        return none

    def pformat(self, obj: Any) -> Str:
        return Str(self._impl.pformat(obj))

    def isreadable(self, obj: Any) -> Boolean:
        return true if self._impl.isreadable(obj) else false

    def isrecursive(self, obj: Any) -> Boolean:
        return true if self._impl.isrecursive(obj) else false


class Pprint:
    """Namespace mirroring Python's `pprint` module — multi-line,
    indented printing of nested data structures.

    Output traverses each object's `__repr__`. POOP types alias
    `__repr__` to `__str__`, so pretty-printed output reads like
    POOP's regular `Object.print()`.
    """

    @staticmethod
    def pprint(
        obj: Any,
        *,
        indent: Int | None = None,
        width: Int | None = None,
        depth: Int | None = None,
        compact: Boolean | None = None,
        sort_dicts: Boolean | None = None,
        underscore_numbers: Boolean | None = None,
    ) -> NoneClass:
        _pprint.pprint(
            obj,
            indent=_i(indent, 1) or 1,
            width=_i(width, 80) or 80,
            depth=_i(depth, None),
            compact=_b(compact, False),
            sort_dicts=_b(sort_dicts, True),
            underscore_numbers=_b(underscore_numbers, False),
        )
        return none

    @staticmethod
    def pformat(
        obj: Any,
        *,
        indent: Int | None = None,
        width: Int | None = None,
        depth: Int | None = None,
        compact: Boolean | None = None,
        sort_dicts: Boolean | None = None,
        underscore_numbers: Boolean | None = None,
    ) -> Str:
        return Str(
            _pprint.pformat(
                obj,
                indent=_i(indent, 1) or 1,
                width=_i(width, 80) or 80,
                depth=_i(depth, None),
                compact=_b(compact, False),
                sort_dicts=_b(sort_dicts, True),
                underscore_numbers=_b(underscore_numbers, False),
            )
        )

    @staticmethod
    def pp(
        obj: Any,
        *,
        indent: Int | None = None,
        width: Int | None = None,
        depth: Int | None = None,
        compact: Boolean | None = None,
        sort_dicts: Boolean | None = None,
        underscore_numbers: Boolean | None = None,
    ) -> NoneClass:
        # pp differs from pprint only in default sort_dicts=False.
        sd = false if sort_dicts is None else sort_dicts
        return Pprint.pprint(
            obj,
            indent=indent,
            width=width,
            depth=depth,
            compact=compact,
            sort_dicts=sd,
            underscore_numbers=underscore_numbers,
        )

    @staticmethod
    def isreadable(obj: Any) -> Boolean:
        return true if _pprint.isreadable(obj) else false

    @staticmethod
    def isrecursive(obj: Any) -> Boolean:
        return true if _pprint.isrecursive(obj) else false

    @staticmethod
    def saferepr(obj: Any) -> Str:
        return Str(_pprint.saferepr(obj))
