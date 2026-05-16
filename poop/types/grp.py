from __future__ import annotations

import grp as _grp
from typing import Any, ClassVar

from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.string import Str


class Group(Object):
    """Wraps Python's `grp.struct_group` — one Unix group-file entry."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def gr_name(self) -> Str:
        return Str(self._impl.gr_name)

    @property
    def gr_passwd(self) -> Str:
        return Str(self._impl.gr_passwd)

    @property
    def gr_gid(self) -> Int:
        return Int(self._impl.gr_gid)

    @property
    def gr_mem(self) -> List:
        return List(*(Str(member) for member in self._impl.gr_mem))

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class Grp:
    """Namespace mirroring Python's `grp` module — Unix group-file lookups."""

    Group: ClassVar[type[Group]] = Group

    @staticmethod
    def getgrgid(gid: Int) -> Group:
        return Group(_grp.getgrgid(gid._value))

    @staticmethod
    def getgrnam(name: Str) -> Group:
        return Group(_grp.getgrnam(name._value))

    @staticmethod
    def getgrall() -> List:
        return List(*(Group(entry) for entry in _grp.getgrall()))
