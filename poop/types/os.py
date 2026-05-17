from __future__ import annotations

import os as _os
from typing import ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.path import Path
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


def _path_str(p: Path | Str) -> str:
    return p._value if isinstance(p, Str) else str(p)


class Env:
    """Namespace mirroring access to environment variables (`os.environ`)."""

    @staticmethod
    def get(key: Str, default: Str | NoneClass | None = None) -> Str | NoneClass:
        if default is None or isinstance(default, NoneClass):
            val = _os.environ.get(key._value)
        else:
            val = _os.environ.get(key._value, default._value)
        if val is None:
            return none
        return Str(val)

    @staticmethod
    def set(key: Str, value: Str) -> NoneClass:
        _os.environ[key._value] = value._value
        return none

    @staticmethod
    def unset(key: Str) -> NoneClass:
        _os.environ.pop(key._value, None)
        return none

    @staticmethod
    def has(key: Str) -> Boolean:
        return true if key._value in _os.environ else false

    @staticmethod
    def keys() -> Set:
        return Set(*(Str(k) for k in _os.environ.keys()))

    @staticmethod
    def values() -> List:
        return List(*(Str(v) for v in _os.environ.values()))

    @staticmethod
    def as_dict() -> Dict:
        d = Dict()
        for k, v in _os.environ.items():
            d.at_put(Str(k), Str(v))
        return d


class Process:
    """Namespace mirroring current-process operations from `os`."""

    @staticmethod
    def pid() -> Int:
        return Int(_os.getpid())

    @staticmethod
    def ppid() -> Int:
        return Int(_os.getppid())

    @staticmethod
    def uid() -> Int:
        return Int(_os.getuid())

    @staticmethod
    def gid() -> Int:
        return Int(_os.getgid())

    @staticmethod
    def euid() -> Int:
        return Int(_os.geteuid())

    @staticmethod
    def egid() -> Int:
        return Int(_os.getegid())

    @staticmethod
    def umask(mask: Int) -> Int:
        return Int(_os.umask(mask._value))

    @staticmethod
    def chdir(path: Path | Str) -> NoneClass:
        _os.chdir(_path_str(path))
        return none

    @staticmethod
    def getcwd() -> Path:
        return Path(Str(_os.getcwd()))

    @staticmethod
    def kill(pid: Int, signal: Int) -> NoneClass:
        _os.kill(pid._value, signal._value)
        return none


class OS:
    """Namespace mirroring (a curated subset of) Python's `os` module.

    Most filesystem ops live on `Path`. The `os` namespace exposes
    only what `Path` doesn't cover: random bytes, CPU counts,
    load average, and a small set of low-level constants.
    `os.path` is intentionally absent — use `Path`.
    Process state lives on `process`; environment lives on `env`.
    """

    process: ClassVar[type[Process]] = Process
    env: ClassVar[type[Env]] = Env

    # Path-mode flags for access() / open()
    F_OK: ClassVar[Int] = Int(_os.F_OK)
    R_OK: ClassVar[Int] = Int(_os.R_OK)
    W_OK: ClassVar[Int] = Int(_os.W_OK)
    X_OK: ClassVar[Int] = Int(_os.X_OK)

    # Open flags
    O_RDONLY: ClassVar[Int] = Int(_os.O_RDONLY)
    O_WRONLY: ClassVar[Int] = Int(_os.O_WRONLY)
    O_RDWR: ClassVar[Int] = Int(_os.O_RDWR)
    O_APPEND: ClassVar[Int] = Int(_os.O_APPEND)
    O_CREAT: ClassVar[Int] = Int(_os.O_CREAT)
    O_TRUNC: ClassVar[Int] = Int(_os.O_TRUNC)
    O_EXCL: ClassVar[Int] = Int(_os.O_EXCL)

    # Path separators
    sep: ClassVar[Str] = Str(_os.sep)
    linesep: ClassVar[Str] = Str(_os.linesep)
    pathsep: ClassVar[Str] = Str(_os.pathsep)
    devnull: ClassVar[Str] = Str(_os.devnull)

    @staticmethod
    def urandom(n: Int) -> Bytes:
        return Bytes(_os.urandom(n._value))

    @staticmethod
    def cpu_count() -> Int | NoneClass:
        n = _os.cpu_count()
        return none if n is None else Int(n)

    @staticmethod
    def process_cpu_count() -> Int | NoneClass:
        n = _os.process_cpu_count()
        return none if n is None else Int(n)

    @staticmethod
    def getloadavg() -> Tuple:
        a, b, c = _os.getloadavg()
        return Tuple(Float(a), Float(b), Float(c))
