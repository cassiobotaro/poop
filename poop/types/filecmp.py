from __future__ import annotations

import filecmp as _filecmp
import io as _io
from contextlib import redirect_stdout
from typing import Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types.boolean import Boolean, to_boolean, true
from poop.types.dict import Dict
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _path_str(p: Path | Str) -> str:
    if isinstance(p, Path):
        return str(p._path)
    return p._value


def _unwrap_str_list(seq: List | Tuple | None) -> list[str] | None:
    if seq is None:
        return None
    result: list[str] = []
    for item in seq:
        if not isinstance(item, Str):
            raise TypeError(f"expected Str entries, got {type(item).__name__}")
        result.append(item._value)
    return result


def _wrap_str_list(items: list[str]) -> List:
    return List(*(Str(s) for s in items))


class Dircmp(_ImplWrapperMixin, Object):
    """Wraps Python's `filecmp.dircmp` for recursive directory comparison.

    `Dircmp(a, b, ignore=none, hide=none)` builds a comparison tree
    keyed on file names. Attributes expose the categorized name
    groups (`left_only`, `right_only`, `common`, `diff_files`,
    `same_files`, `funny_files`, `common_dirs`, `common_files`,
    `common_funny`) and the `.subdirs` recurses into per-directory
    `Dircmp` instances. `.report*` writes the comparison summary to
    stdout (or returns it via `report_str` if you'd rather capture).
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        a: Path | Str,
        b: Path | Str,
        ignore: List | Tuple | None = None,
        hide: List | Tuple | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        ignore_list = _unwrap_str_list(ignore)
        hide_list = _unwrap_str_list(hide)
        if ignore_list is not None:
            kwargs["ignore"] = ignore_list
        if hide_list is not None:
            kwargs["hide"] = hide_list
        self._impl = _filecmp.dircmp(_path_str(a), _path_str(b), **kwargs)

    @property
    def left(self) -> Str:
        return Str(self._impl.left)

    @property
    def right(self) -> Str:
        return Str(self._impl.right)

    @property
    def left_only(self) -> List:
        return _wrap_str_list(self._impl.left_only)

    @property
    def right_only(self) -> List:
        return _wrap_str_list(self._impl.right_only)

    @property
    def common(self) -> List:
        return _wrap_str_list(self._impl.common)

    @property
    def common_dirs(self) -> List:
        return _wrap_str_list(self._impl.common_dirs)

    @property
    def common_files(self) -> List:
        return _wrap_str_list(self._impl.common_files)

    @property
    def common_funny(self) -> List:
        return _wrap_str_list(self._impl.common_funny)

    @property
    def same_files(self) -> List:
        return _wrap_str_list(self._impl.same_files)

    @property
    def diff_files(self) -> List:
        return _wrap_str_list(self._impl.diff_files)

    @property
    def funny_files(self) -> List:
        return _wrap_str_list(self._impl.funny_files)

    @property
    def subdirs(self) -> Dict:
        result = Dict()
        for name, sub in self._impl.subdirs.items():
            result.at_put(Str(name), Dircmp._from_impl(sub))
        return result

    def report(self) -> NoneClass:
        self._impl.report()
        return none

    def report_partial_closure(self) -> NoneClass:
        self._impl.report_partial_closure()
        return none

    def report_full_closure(self) -> NoneClass:
        self._impl.report_full_closure()
        return none

    def report_str(self) -> Str:
        # Capture report() output as Str rather than writing to stdout —
        # useful for tests and for embedding in larger reports.
        buf = _io.StringIO()
        with redirect_stdout(buf):
            self._impl.report()
        return Str(buf.getvalue())


class Filecmp:
    """Namespace mirroring Python's `filecmp` module.

    File-level comparison (`cmp` / `cmpfiles`), the recursive `Dircmp`
    class, and `clear_cache()` to drop the metadata-based fast-path
    cache. The `DEFAULT_IGNORES` list is exposed as a class attribute
    so callers can inspect what `Dircmp` skips by default.
    """

    Dircmp: ClassVar[type[Dircmp]] = Dircmp
    DEFAULT_IGNORES: ClassVar[List]

    @staticmethod
    def cmp(f1: Path | Str, f2: Path | Str, shallow: Boolean | None = None) -> Boolean:
        shallow_v = True if shallow is None else bool(shallow)
        return to_boolean(_filecmp.cmp(_path_str(f1), _path_str(f2), shallow_v))

    @staticmethod
    def cmpfiles(
        a: Path | Str,
        b: Path | Str,
        common: List | Tuple,
        shallow: Boolean = true,
    ) -> Tuple:
        match, mismatch, errors = _filecmp.cmpfiles(
            _path_str(a),
            _path_str(b),
            _unwrap_str_list(common) or [],
            bool(shallow),
        )
        return Tuple(
            _wrap_str_list(match),
            _wrap_str_list(mismatch),
            _wrap_str_list(errors),
        )

    @staticmethod
    def clear_cache() -> NoneClass:
        _filecmp.clear_cache()
        return none


# Snapshot the upstream default-ignore list once at import.
Filecmp.DEFAULT_IGNORES = _wrap_str_list(list(_filecmp.DEFAULT_IGNORES))
