from __future__ import annotations

import os as _os
from collections.abc import Callable
from typing import Any, ClassVar

from poop.types._bridge import bridge
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


class Environ:
    """Namespace mirroring `os.environ` — environment-variable access.

    POOP forbids subscript syntax, so Python's `os.environ["X"] = "y"`
    becomes the explicit `os.environ.set("X", "y")`.
    """

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


class OS:
    """Namespace mirroring (a curated subset of) Python's `os` module.

    Most filesystem ops live on `Path`; `os.path` is intentionally
    absent. Environment access is grouped under the `os.environ`
    sub-namespace (mirroring Python's `os.environ` attribute).
    """

    environ: ClassVar[type[Environ]] = Environ

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

    # --- Random / CPU helpers ---

    @staticmethod
    def urandom(size: Int, /) -> Bytes:
        return Bytes(_os.urandom(size._value))

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

    # --- Process state (mirroring Python's os.* directly) ---

    @staticmethod
    def getpid() -> Int:
        return Int(_os.getpid())

    @staticmethod
    def getppid() -> Int:
        return Int(_os.getppid())

    @staticmethod
    def getuid() -> Int:
        return Int(_os.getuid())

    @staticmethod
    def getgid() -> Int:
        return Int(_os.getgid())

    @staticmethod
    def geteuid() -> Int:
        return Int(_os.geteuid())

    @staticmethod
    def getegid() -> Int:
        return Int(_os.getegid())

    @staticmethod
    def umask(mask: Int) -> Int:
        return Int(_os.umask(mask._value))

    @staticmethod
    def chmod(
        path: Path | Str, mode: Int, follow_symlinks: Boolean = true
    ) -> NoneClass:
        _os.chmod(_path_str(path), mode._value, follow_symlinks=bool(follow_symlinks))
        return none

    @staticmethod
    def chown(
        path: Path | Str,
        uid: Int,
        gid: Int,
        follow_symlinks: Boolean = true,
    ) -> NoneClass:
        _os.chown(
            _path_str(path),
            uid._value,
            gid._value,
            follow_symlinks=bool(follow_symlinks),
        )
        return none

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

    @staticmethod
    def walk(
        top: Path | Str,
        topdown: Boolean = true,
        onerror: Callable[..., Any] | None = None,
        followlinks: Boolean = false,
    ) -> List:
        """Eager `os.walk`. Returns a `List` of `Tuple(root, dirs, files)`.

        `root` is a `Path`; `dirs` / `files` are `List[Str]` of basenames.
        `onerror` accepts a POOP `Block` routed through `block.bridge` —
        the block receives an `OSError` (raw Python exception, mirroring
        CPython's contract) and can re-raise or log.
        """
        py_onerror = None if onerror is None else bridge(onerror)
        out: list[Tuple] = []
        for root, dirs, files in _os.walk(
            _path_str(top),
            topdown=bool(topdown),
            onerror=py_onerror,
            followlinks=bool(followlinks),
        ):
            out.append(
                Tuple(
                    Path(Str(root)),
                    List(*(Str(d) for d in dirs)),
                    List(*(Str(f) for f in files)),
                )
            )
        return List(*out)
