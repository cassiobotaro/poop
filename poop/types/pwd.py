from __future__ import annotations

import pwd as _pwd
from typing import Any, ClassVar

from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.string import Str


class Passwd(Object):
    """Wraps Python's `pwd.struct_passwd` — one Unix password-file entry."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def pw_name(self) -> Str:
        return Str(self._impl.pw_name)

    @property
    def pw_passwd(self) -> Str:
        return Str(self._impl.pw_passwd)

    @property
    def pw_uid(self) -> Int:
        return Int(self._impl.pw_uid)

    @property
    def pw_gid(self) -> Int:
        return Int(self._impl.pw_gid)

    @property
    def pw_gecos(self) -> Str:
        return Str(self._impl.pw_gecos)

    @property
    def pw_dir(self) -> Str:
        return Str(self._impl.pw_dir)

    @property
    def pw_shell(self) -> Str:
        return Str(self._impl.pw_shell)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class Pwd:
    """Namespace mirroring Python's `pwd` module — Unix password-file
    lookups.

    Each lookup returns a `Passwd` POOP record. `getpwall` materializes
    the full database into a `List[Passwd]`.
    """

    Passwd: ClassVar[type[Passwd]] = Passwd

    @staticmethod
    def getpwuid(uidobj: Int, /) -> Passwd:
        return Passwd(_pwd.getpwuid(uidobj._value))

    @staticmethod
    def getpwnam(name: Str) -> Passwd:
        return Passwd(_pwd.getpwnam(name._value))

    @staticmethod
    def getpwall() -> List:
        return List(*(Passwd(entry) for entry in _pwd.getpwall()))
