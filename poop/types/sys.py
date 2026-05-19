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
    """Snapshot of `sys.modules` mapping name → file path (or `none`).

    The original dict held raw CPython module objects as values, which
    leaked the Python module type through POOP's surface. The file path
    is the only field user code typically cares about; everything else
    is reachable through `imports` / dedicated wrappers.
    """
    d = Dict()
    for k, v in list(_sys.modules.items()):
        path = getattr(v, "__file__", None)
        d.at_put(Str(k), Str(path) if isinstance(path, str) else none)
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


class _SysNamespace:
    """Singleton namespace mirroring (a curated subset of) Python's `sys` module.

    Python `sys` attributes (`sys.argv`, `sys.platform`, `sys.modules`, …)
    are exposed as POOP `@property` attributes so user code reads the
    same `sys.argv` / `sys.platform` it would in Python. Real callables
    (`sys.exit`, `sys.getrecursionlimit`) stay as methods.

    The introspection-heavy pieces (`settrace` / `_getframe` /
    `monitoring` / `audit*`) are deliberately out of scope.
    """

    @property
    def argv(self) -> List:
        return List(*(Str(a) for a in _sys.argv))

    @property
    def stdout(self) -> Stdout:
        return Stdout(_sys.stdout)

    @property
    def stderr(self) -> Stdout:
        return Stdout(_sys.stderr)

    @property
    def stdin(self) -> Stdin:
        return Stdin(_sys.stdin)

    @property
    def executable(self) -> Path:
        return Path(Str(_sys.executable))

    @property
    def platform(self) -> Str:
        return Str(_sys.platform)

    @property
    def version(self) -> Str:
        return Str(_sys.version)

    @property
    def version_info(self) -> Tuple:
        return _wrap_version_info()

    @property
    def implementation(self) -> Any:
        return _sys.implementation

    @property
    def maxsize(self) -> Int:
        return Int(_sys.maxsize)

    @property
    def byteorder(self) -> Str:
        return Str(_sys.byteorder)

    @property
    def flags(self) -> Any:
        return _sys.flags

    @property
    def float_info(self) -> Any:
        return _sys.float_info

    @property
    def int_info(self) -> Any:
        return _sys.int_info

    @property
    def hash_info(self) -> Any:
        return _sys.hash_info

    @property
    def thread_info(self) -> Any:
        return _sys.thread_info

    @property
    def modules(self) -> Dict:
        return _modules_dict()

    @property
    def path(self) -> List:
        return _path_list()

    def exit(self, status: Int | Str | None = None, /) -> NoneClass:
        if status is None:
            _sys.exit()
        elif isinstance(status, Int | Str):
            _sys.exit(status._value)
        else:
            _sys.exit(status)
        return none  # pragma: no cover

    def getrecursionlimit(self) -> Int:
        return Int(_sys.getrecursionlimit())

    def setrecursionlimit(self, limit: Int) -> NoneClass:
        _sys.setrecursionlimit(limit._value)
        return none


Sys = _SysNamespace()
