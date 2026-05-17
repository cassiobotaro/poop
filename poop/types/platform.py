from __future__ import annotations

import platform as _platform
from typing import Any, ClassVar

from poop.types.boolean import Boolean
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


class Uname(Object):
    """Wraps Python's `platform.uname_result` — system identification."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def system(self) -> Str:
        return Str(self._impl.system)

    @property
    def node(self) -> Str:
        return Str(self._impl.node)

    @property
    def release(self) -> Str:
        return Str(self._impl.release)

    @property
    def version(self) -> Str:
        return Str(self._impl.version)

    @property
    def machine(self) -> Str:
        return Str(self._impl.machine)

    @property
    def processor(self) -> Str:
        return Str(self._impl.processor)


class Platform:
    """Namespace mirroring Python's `platform` module."""

    Uname: ClassVar[type[Uname]] = Uname

    @staticmethod
    def system() -> Str:
        return Str(_platform.system())

    @staticmethod
    def release() -> Str:
        return Str(_platform.release())

    @staticmethod
    def version() -> Str:
        return Str(_platform.version())

    @staticmethod
    def machine() -> Str:
        return Str(_platform.machine())

    @staticmethod
    def processor() -> Str:
        return Str(_platform.processor())

    @staticmethod
    def node() -> Str:
        return Str(_platform.node())

    @staticmethod
    def platform(aliased: Boolean | None = None, terse: Boolean | None = None) -> Str:
        a = False if aliased is None else bool(aliased)
        t = False if terse is None else bool(terse)
        return Str(_platform.platform(aliased=a, terse=t))

    @staticmethod
    def uname() -> Uname:
        return Uname(_platform.uname())

    @staticmethod
    def architecture() -> Tuple:
        bits, linkage = _platform.architecture()
        return Tuple(Str(bits), Str(linkage))

    @staticmethod
    def python_version() -> Str:
        return Str(_platform.python_version())

    @staticmethod
    def python_version_tuple() -> Tuple:
        return Tuple(*(Str(s) for s in _platform.python_version_tuple()))

    @staticmethod
    def python_branch() -> Str:
        return Str(_platform.python_branch())

    @staticmethod
    def python_build() -> Tuple:
        a, b = _platform.python_build()
        return Tuple(Str(a), Str(b))

    @staticmethod
    def python_compiler() -> Str:
        return Str(_platform.python_compiler())

    @staticmethod
    def python_implementation() -> Str:
        return Str(_platform.python_implementation())

    @staticmethod
    def python_revision() -> Str:
        return Str(_platform.python_revision())

    @staticmethod
    def mac_ver() -> Tuple:
        release, versioninfo, machine = _platform.mac_ver()
        vi = Tuple(*(Str(s) for s in versioninfo))
        return Tuple(Str(release), vi, Str(machine))

    @staticmethod
    def win32_ver() -> Tuple:
        release, version, csd, ptype = _platform.win32_ver()
        return Tuple(Str(release), Str(version), Str(csd), Str(ptype))

    @staticmethod
    def libc_ver() -> Tuple:
        lib, version = _platform.libc_ver()
        return Tuple(Str(lib), Str(version))
