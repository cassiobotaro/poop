from __future__ import annotations

import sys as _sys
from typing import Any

from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _wrap_version_info() -> Tuple:
    vi = _sys.version_info
    return Tuple(
        Int(vi.major),
        Int(vi.minor),
        Int(vi.micro),
        Str(vi.releaselevel),
        Int(vi.serial),
    )


def _modules_dict() -> Dict:
    d = Dict()
    for k, v in list(_sys.modules.items()):
        d.at_put(Str(k), v)  # ty: ignore[invalid-argument-type]
    return d


def _path_list() -> List:
    return List(*(Str(p) for p in _sys.path))


class Stdout(Object):
    """Wraps `sys.stdout` for line-oriented writing."""

    __slots__ = ("_stream",)

    def __init__(self, stream: Any) -> None:
        self._stream = stream

    def write(self, s: Str) -> Int:
        return Int(self._stream.write(s._value))

    def writeln(self, s: Str | None = None) -> NoneClass:
        text = "" if s is None else s._value
        self._stream.write(text + "\n")
        return none

    def flush(self) -> NoneClass:
        self._stream.flush()
        return none

    def isatty(self) -> Boolean:
        return true if self._stream.isatty() else false


class Stdin(Object):
    """Wraps `sys.stdin` for line-oriented reading."""

    __slots__ = ("_stream",)

    def __init__(self, stream: Any) -> None:
        self._stream = stream

    def read(self, size: Int | None = None) -> Str:
        if size is None:
            return Str(self._stream.read())
        return Str(self._stream.read(size._value))

    def readline(self, size: Int | None = None) -> Str:
        if size is None:
            return Str(self._stream.readline())
        return Str(self._stream.readline(size._value))

    def readlines(self) -> List:
        return List(*(Str(line) for line in self._stream.readlines()))

    def isatty(self) -> Boolean:
        return true if self._stream.isatty() else false

    def __iter__(self) -> Any:
        for line in self._stream:
            yield Str(line)


class Sys:
    """Namespace mirroring (a curated subset of) Python's `sys` module.

    The introspection-heavy pieces (`settrace` / `_getframe` /
    `monitoring` / `audit*`) are deliberately out of scope. POOP's
    method-call shape means Python attributes like `sys.argv` /
    `sys.platform` become callables (`sys.argv()`, `sys.platform()`)
    that return POOP types.
    """

    @staticmethod
    def argv() -> List:
        return List(*(Str(a) for a in _sys.argv))

    @staticmethod
    def stdout() -> Stdout:
        return Stdout(_sys.stdout)

    @staticmethod
    def stderr() -> Stdout:
        return Stdout(_sys.stderr)

    @staticmethod
    def stdin() -> Stdin:
        return Stdin(_sys.stdin)

    @staticmethod
    def exit(code: Int | Str | None = None) -> NoneClass:
        if code is None:
            _sys.exit()
        elif isinstance(code, Int | Str):
            _sys.exit(code._value)
        else:
            _sys.exit(code)
        return none  # pragma: no cover

    @staticmethod
    def executable() -> Path:
        return Path(Str(_sys.executable))

    @staticmethod
    def platform() -> Str:
        return Str(_sys.platform)

    @staticmethod
    def version() -> Str:
        return Str(_sys.version)

    @staticmethod
    def version_info() -> Tuple:
        return _wrap_version_info()

    @staticmethod
    def implementation() -> Any:
        return _sys.implementation

    @staticmethod
    def maxsize() -> Int:
        return Int(_sys.maxsize)

    @staticmethod
    def byteorder() -> Str:
        return Str(_sys.byteorder)

    @staticmethod
    def flags() -> Any:
        return _sys.flags

    @staticmethod
    def float_info() -> Any:
        return _sys.float_info

    @staticmethod
    def int_info() -> Any:
        return _sys.int_info

    @staticmethod
    def hash_info() -> Any:
        return _sys.hash_info

    @staticmethod
    def thread_info() -> Any:
        return _sys.thread_info

    @staticmethod
    def modules() -> Dict:
        return _modules_dict()

    @staticmethod
    def path() -> List:
        return _path_list()

    @staticmethod
    def getrecursionlimit() -> Int:
        return Int(_sys.getrecursionlimit())

    @staticmethod
    def setrecursionlimit(limit: Int) -> NoneClass:
        _sys.setrecursionlimit(limit._value)
        return none
