from __future__ import annotations

import re as _re
import sys as _sys
from typing import Any, ClassVar

from poop.types._unwrap import _opt_int, _unwrap
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _wrap_match(m: _re.Match[str] | None) -> Match | NoneClass:
    return none if m is None else Match(m)


def _wrap_group_value(value: str | None) -> Str | NoneClass:
    return none if value is None else Str(value)


def _unwrap_repl(repl: Str) -> str:
    return repl._value


class Match(Object):
    """Wraps Python's `re.Match` — the result of a successful regex
    match. Mirrors CPython's API surface."""

    __slots__ = ("_impl",)

    def __init__(self, impl: _re.Match[str]) -> None:
        self._impl = impl

    def group(self, *args: Int | Str) -> Str | NoneClass | Tuple:
        if len(args) == 0:
            return Str(self._impl.group())
        if len(args) == 1:
            key = args[0]._value
            return _wrap_group_value(self._impl.group(key))
        return Tuple(*[_wrap_group_value(self._impl.group(a._value)) for a in args])

    def groups(self, default: Str | NoneClass | None = None) -> Tuple:
        default_value: Any = _unwrap(default, None)
        return Tuple(
            *[
                Str(g) if g is not None else (default if default is not None else none)
                for g in self._impl.groups(default_value)
            ]
        )

    def groupdict(self, default: Str | NoneClass | None = None) -> Dict:
        default_value: Any = _unwrap(default, None)
        raw = self._impl.groupdict(default_value)
        result = Dict()
        for k, v in raw.items():
            if v is None:
                result.at_put(Str(k), default if default is not None else none)
            else:
                result.at_put(Str(k), Str(v))
        return result

    def start(self, group: Int | NoneClass | None = None) -> Int:
        idx = _unwrap(group, 0)
        return Int(self._impl.start(idx))

    def end(self, group: Int | NoneClass | None = None) -> Int:
        idx = _unwrap(group, 0)
        return Int(self._impl.end(idx))

    def span(self, group: Int | NoneClass | None = None) -> Tuple:
        idx = _unwrap(group, 0)
        a, b = self._impl.span(idx)
        return Tuple(Int(a), Int(b))

    def expand(self, template: Str) -> Str:
        return Str(self._impl.expand(template._value))

    @property
    def string(self) -> Str:
        return Str(self._impl.string)

    @property
    def re(self) -> Pattern:
        return Pattern(self._impl.re)


def _findall_result(raw: list[Any]) -> List:
    out: list[Any] = []
    for item in raw:
        if isinstance(item, tuple):
            out.append(Tuple(*[Str(s) for s in item]))
        else:
            out.append(Str(item))
    return List(*out)


class Pattern(Object):
    """Wraps Python's `re.Pattern` — a compiled regular expression.
    Built by `re.compile(...)` or accessed via `Match.re`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: _re.Pattern[str]) -> None:
        self._impl = impl

    def match(
        self,
        string: Str,
        pos: Int | NoneClass | None = None,
        endpos: Int | NoneClass | None = None,
    ) -> Match | NoneClass:
        return _wrap_match(
            self._impl.match(
                string._value, _opt_int(pos, 0), _opt_int(endpos, _sys.maxsize)
            )
        )

    def search(
        self,
        string: Str,
        pos: Int | NoneClass | None = None,
        endpos: Int | NoneClass | None = None,
    ) -> Match | NoneClass:
        return _wrap_match(
            self._impl.search(
                string._value, _opt_int(pos, 0), _opt_int(endpos, _sys.maxsize)
            )
        )

    def fullmatch(
        self,
        string: Str,
        pos: Int | NoneClass | None = None,
        endpos: Int | NoneClass | None = None,
    ) -> Match | NoneClass:
        return _wrap_match(
            self._impl.fullmatch(
                string._value, _opt_int(pos, 0), _opt_int(endpos, _sys.maxsize)
            )
        )

    def findall(
        self,
        string: Str,
        pos: Int | NoneClass | None = None,
        endpos: Int | NoneClass | None = None,
    ) -> List:
        return _findall_result(
            self._impl.findall(
                string._value, _opt_int(pos, 0), _opt_int(endpos, _sys.maxsize)
            )
        )

    def finditer(
        self,
        string: Str,
        pos: Int | NoneClass | None = None,
        endpos: Int | NoneClass | None = None,
    ) -> Tuple:
        return Tuple(
            *[
                Match(m)
                for m in self._impl.finditer(
                    string._value, _opt_int(pos, 0), _opt_int(endpos, _sys.maxsize)
                )
            ]
        )

    def sub(self, repl: Str, string: Str, count: Int | NoneClass | None = None) -> Str:
        n = _unwrap(count, 0)
        return Str(self._impl.sub(_unwrap_repl(repl), string._value, n))

    def subn(
        self, repl: Str, string: Str, count: Int | NoneClass | None = None
    ) -> Tuple:
        n = _unwrap(count, 0)
        new, num = self._impl.subn(_unwrap_repl(repl), string._value, n)
        return Tuple(Str(new), Int(num))

    def split(self, string: Str, maxsplit: Int | NoneClass | None = None) -> List:
        n = _unwrap(maxsplit, 0)
        return List(
            *[
                Str(p) if p is not None else none
                for p in self._impl.split(string._value, n)
            ]
        )

    @property
    def pattern(self) -> Str:
        return Str(self._impl.pattern)

    @property
    def flags(self) -> Int:
        return Int(self._impl.flags)

    @property
    def groups(self) -> Int:
        return Int(self._impl.groups)

    @property
    def groupindex(self) -> Dict:
        result = Dict()
        for k, v in self._impl.groupindex.items():
            result.at_put(Str(k), Int(v))
        return result


class Re:
    """Namespace mirroring Python's `re` module — regular expression
    operations on `Str`."""

    IGNORECASE: ClassVar[Int] = Int(int(_re.IGNORECASE))
    MULTILINE: ClassVar[Int] = Int(int(_re.MULTILINE))
    DOTALL: ClassVar[Int] = Int(int(_re.DOTALL))
    VERBOSE: ClassVar[Int] = Int(int(_re.VERBOSE))
    ASCII: ClassVar[Int] = Int(int(_re.ASCII))
    UNICODE: ClassVar[Int] = Int(int(_re.UNICODE))
    LOCALE: ClassVar[Int] = Int(int(_re.LOCALE))
    DEBUG: ClassVar[Int] = Int(int(_re.DEBUG))
    NOFLAG: ClassVar[Int] = Int(int(_re.NOFLAG))

    Pattern: ClassVar[type[Pattern]] = Pattern
    Match: ClassVar[type[Match]] = Match

    # Exception class — caught via Try.except_(re.error, ...).
    error: ClassVar[type[Exception]] = _re.error

    @staticmethod
    def purge() -> NoneClass:
        """Clear the regular expression cache."""
        _re.purge()
        return none

    @staticmethod
    def compile(pattern: Str, flags: Int | NoneClass | None = None) -> Pattern:
        return Pattern(_re.compile(pattern._value, _unwrap(flags, 0)))

    @staticmethod
    def match(
        pattern: Str, string: Str, flags: Int | NoneClass | None = None
    ) -> Match | NoneClass:
        return _wrap_match(_re.match(pattern._value, string._value, _unwrap(flags, 0)))

    @staticmethod
    def search(
        pattern: Str, string: Str, flags: Int | NoneClass | None = None
    ) -> Match | NoneClass:
        return _wrap_match(_re.search(pattern._value, string._value, _unwrap(flags, 0)))

    @staticmethod
    def fullmatch(
        pattern: Str, string: Str, flags: Int | NoneClass | None = None
    ) -> Match | NoneClass:
        return _wrap_match(
            _re.fullmatch(pattern._value, string._value, _unwrap(flags, 0))
        )

    @staticmethod
    def findall(
        pattern: Str, string: Str, flags: Int | NoneClass | None = None
    ) -> List:
        return _findall_result(
            _re.findall(pattern._value, string._value, _unwrap(flags, 0))
        )

    @staticmethod
    def finditer(
        pattern: Str, string: Str, flags: Int | NoneClass | None = None
    ) -> Tuple:
        return Tuple(
            *[
                Match(m)
                for m in _re.finditer(pattern._value, string._value, _unwrap(flags, 0))
            ]
        )

    @staticmethod
    def sub(
        pattern: Str,
        repl: Str,
        string: Str,
        count: Int | NoneClass | None = None,
        flags: Int | NoneClass | None = None,
    ) -> Str:
        return Str(
            _re.sub(
                pattern._value,
                _unwrap_repl(repl),
                string._value,
                count=_unwrap(count, 0),
                flags=_unwrap(flags, 0),
            )
        )

    @staticmethod
    def subn(
        pattern: Str,
        repl: Str,
        string: Str,
        count: Int | NoneClass | None = None,
        flags: Int | NoneClass | None = None,
    ) -> Tuple:
        new, num = _re.subn(
            pattern._value,
            _unwrap_repl(repl),
            string._value,
            count=_unwrap(count, 0),
            flags=_unwrap(flags, 0),
        )
        return Tuple(Str(new), Int(num))

    @staticmethod
    def split(
        pattern: Str,
        string: Str,
        maxsplit: Int | NoneClass | None = None,
        flags: Int | NoneClass | None = None,
    ) -> List:
        parts = _re.split(
            pattern._value,
            string._value,
            maxsplit=_unwrap(maxsplit, 0),
            flags=_unwrap(flags, 0),
        )
        return List(*[Str(p) if p is not None else none for p in parts])

    @staticmethod
    def escape(pattern: Str) -> Str:
        return Str(_re.escape(pattern._value))
