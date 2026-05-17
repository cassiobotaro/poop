from __future__ import annotations

import cProfile as _cProfile
import io as _io
import pstats as _pstats
from typing import Any, ClassVar, Self

from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


class Profile(Object):
    """Wraps Python's `cProfile.Profile` — deterministic profiler."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any = None) -> None:
        self._impl = _cProfile.Profile() if impl is None else impl

    def enable(self) -> NoneClass:
        self._impl.enable()
        return none

    def disable(self) -> NoneClass:
        self._impl.disable()
        return none

    def create_stats(self) -> NoneClass:
        self._impl.create_stats()
        return none

    def dump_stats(self, file: Path | Str) -> NoneClass:
        path = file._value if isinstance(file, Str) else str(file)
        self._impl.dump_stats(path)
        return none

    def print_stats(self) -> Str:
        buf = _io.StringIO()
        stats = _pstats.Stats(self._impl, stream=buf)
        stats.print_stats()
        return Str(buf.getvalue())

    def runcall(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        return self._impl.runcall(func, *args, **kwargs)

    def __enter__(self) -> Self:
        self.enable()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.disable()


class CProfile:
    """Namespace mirroring Python's `cProfile` module."""

    Profile: ClassVar[type[Profile]] = Profile

    @staticmethod
    def run(
        statement: Str,
        filename: Path | Str | None = None,
        sort: Int = Int(-1),
    ) -> NoneClass:
        path = (
            None
            if filename is None
            else (filename._value if isinstance(filename, Str) else str(filename))
        )
        _cProfile.run(statement._value, filename=path, sort=sort._value)
        return none


class SortKey:
    """Mirror of `pstats.SortKey` — sort keys as POOP `Str` values."""

    CALLS: ClassVar[Str] = Str("calls")
    CUMULATIVE: ClassVar[Str] = Str("cumulative")
    FILENAME: ClassVar[Str] = Str("filename")
    LINE: ClassVar[Str] = Str("line")
    NAME: ClassVar[Str] = Str("name")
    NFL: ClassVar[Str] = Str("nfl")
    PCALLS: ClassVar[Str] = Str("pcalls")
    STDNAME: ClassVar[Str] = Str("stdname")
    TIME: ClassVar[Str] = Str("time")


class Stats(Object):
    """Wraps Python's `pstats.Stats`."""

    __slots__ = ("_impl", "_buf")

    def __init__(self, source: Profile | Path | Str | Any) -> None:
        self._buf = _io.StringIO()
        if isinstance(source, Profile):
            self._impl = _pstats.Stats(source._impl, stream=self._buf)
        elif isinstance(source, Str):
            self._impl = _pstats.Stats(source._value, stream=self._buf)
        elif isinstance(source, Path):
            self._impl = _pstats.Stats(str(source), stream=self._buf)
        else:
            self._impl = _pstats.Stats(source, stream=self._buf)

    def sort_stats(self, *keys: Str) -> Stats:
        self._impl.sort_stats(*(k._value for k in keys))
        return self

    def reverse_order(self) -> Stats:
        self._impl.reverse_order()
        return self

    def strip_dirs(self) -> Stats:
        self._impl.strip_dirs()
        return self

    def print_stats(self) -> Str:
        # Reset stream content for a fresh capture.
        self._buf.seek(0)
        self._buf.truncate()
        self._impl.print_stats()
        return Str(self._buf.getvalue())

    def print_callers(self) -> Str:
        self._buf.seek(0)
        self._buf.truncate()
        self._impl.print_callers()
        return Str(self._buf.getvalue())

    def print_callees(self) -> Str:
        self._buf.seek(0)
        self._buf.truncate()
        self._impl.print_callees()
        return Str(self._buf.getvalue())

    def dump_stats(self, file: Path | Str) -> NoneClass:
        path = file._value if isinstance(file, Str) else str(file)
        self._impl.dump_stats(path)
        return none

    def add(self, *sources: Profile | Path | Str) -> Stats:
        for source in sources:
            if isinstance(source, Profile):
                self._impl.add(source._impl)
            elif isinstance(source, Str):
                self._impl.add(source._value)
            elif isinstance(source, Path):
                self._impl.add(str(source))
            else:
                self._impl.add(source)
        return self


class PStats:
    """Namespace mirroring Python's `pstats` module."""

    Stats: ClassVar[type[Stats]] = Stats
    SortKey: ClassVar[type[SortKey]] = SortKey
