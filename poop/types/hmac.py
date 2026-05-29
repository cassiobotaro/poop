from __future__ import annotations

import hmac as _hmac

from poop.types.boolean import Boolean, to_boolean
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.string import Str


class HMAC:
    """Wraps Python's `hmac.HMAC` keyed-hash MAC.

    Constructed via `hmac.new(...)`. Carries the same surface as the
    Hash objects in `hashlib` (still proposed): `update`, `digest`,
    `hexdigest`, `copy`, plus the `digest_size` / `block_size` /
    `name` attributes.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: _hmac.HMAC) -> None:
        self._impl = impl

    def update(self, msg: Bytes) -> NoneClass:
        self._impl.update(msg._value)
        return none

    def digest(self) -> Bytes:
        return Bytes(self._impl.digest())

    def hexdigest(self) -> Str:
        return Str(self._impl.hexdigest())

    def copy(self) -> HMAC:
        return HMAC(self._impl.copy())

    @property
    def digest_size(self) -> Int:
        return Int(self._impl.digest_size)

    @property
    def block_size(self) -> Int:
        return Int(self._impl.block_size)

    @property
    def name(self) -> Str:
        return Str(self._impl.name)


class Hmac:
    """Namespace mirroring Python's `hmac` module — keyed-hash MAC
    (RFC 2104). Pairs naturally with `hashlib` (still proposed).

    Until `hashlib` ships, `digestmod` accepts a `Str` hash name
    (`"sha256"`, `"sha512"`, …) — CPython's `hmac.new` already
    supports the string form, so this is no divergence.
    """

    @staticmethod
    def new(
        key: Bytes,
        msg: Bytes | None = None,
        digestmod: Str | None = None,
    ) -> HMAC:
        name = "sha256" if digestmod is None else digestmod._value
        msg_value = None if msg is None else msg._value
        return HMAC(_hmac.new(key._value, msg_value, name))

    @staticmethod
    def digest(key: Bytes, msg: Bytes, digest: Str) -> Bytes:
        return Bytes(_hmac.digest(key._value, msg._value, digest._value))

    @staticmethod
    def compare_digest(a: Str | Bytes, b: Str | Bytes, /) -> Boolean:
        return to_boolean(_hmac.compare_digest(a._value, b._value))
