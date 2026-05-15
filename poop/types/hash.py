from __future__ import annotations

import hashlib as _hashlib
from collections.abc import Set as AbstractSet
from typing import Any, ClassVar

from poop.types._unwrap import _unwrap
from poop.types.bytes import Bytes
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.path import Path
from poop.types.string import Str


def _algorithm_names(names: AbstractSet[str]) -> FrozenSet:
    return FrozenSet(*[Str(n) for n in names])


class Hash:
    """Wraps Python's hashlib hash objects.

    Constructed via `hashlib.new(...)`, `hashlib.file_digest(...)` or
    the shortcut messages on `Bytes` (`.sha256()`, `.md5()`, …).
    Mirrors Python's two-step API: `.update()` then
    `.digest()` / `.hexdigest()`.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def update(self, data: Bytes) -> NoneClass:
        self._impl.update(data._value)
        return none

    def digest(self, length: Int | NoneClass | None = None) -> Bytes:
        size = _unwrap(length, None)
        if size is None:
            return Bytes(self._impl.digest())
        return Bytes(self._impl.digest(size))

    def hexdigest(self, length: Int | NoneClass | None = None) -> Str:
        size = _unwrap(length, None)
        if size is None:
            return Str(self._impl.hexdigest())
        return Str(self._impl.hexdigest(size))

    def copy(self) -> Hash:
        return Hash(self._impl.copy())

    @property
    def digest_size(self) -> Int:
        return Int(self._impl.digest_size)

    @property
    def block_size(self) -> Int:
        return Int(self._impl.block_size)

    @property
    def name(self) -> Str:
        return Str(self._impl.name)


class Hashlib:
    """Namespace mirroring Python's `hashlib` module — message digests
    and key-derivation functions.

    Pairs with the shortcut messages on `Bytes` (`.sha256()`,
    `.pbkdf2_hmac(...)`, …); the namespace covers the generic
    constructor, algorithm catalogues and file-digest helper.
    """

    Hash: ClassVar[type[Hash]] = Hash
    algorithms_available: ClassVar[FrozenSet] = _algorithm_names(
        _hashlib.algorithms_available
    )
    algorithms_guaranteed: ClassVar[FrozenSet] = _algorithm_names(
        _hashlib.algorithms_guaranteed
    )

    @staticmethod
    def new(name: Str, data: Bytes | NoneClass | None = None) -> Hash:
        payload = _unwrap(data, b"")
        return Hash(_hashlib.new(name._value, payload))

    @staticmethod
    def file_digest(path: Path, digest: Str, /) -> Hash:
        with path._path.open("rb") as f:
            return Hash(_hashlib.file_digest(f, digest._value))
