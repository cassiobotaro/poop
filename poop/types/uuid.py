from __future__ import annotations

import uuid as _uuid
from typing import TYPE_CHECKING, ClassVar, cast

from poop.types._unwrap import _kwargs_from
from poop.types._value_eq import _ValueEqMixin
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    pass


class UUID(_ValueEqMixin, Object):
    """Wraps Python's `uuid.UUID` as a POOP value.

    Instances are immutable. Construction mirrors `uuid.UUID(...)`
    exactly — pass the canonical string positionally, or use the
    keyword form `UUID(hex=..., bytes=..., int=..., fields=...,
    bytes_le=...)` to parse from the matching representation.
    """

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"
    _impl: _uuid.UUID

    def __init__(
        self,
        hex: Str | None = None,
        bytes: Bytes | None = None,
        bytes_le: Bytes | None = None,
        fields: Tuple | None = None,
        int: Int | None = None,
        version: Int | None = None,
    ) -> None:
        kwargs = _kwargs_from(hex=hex, bytes=bytes, bytes_le=bytes_le)
        if fields is not None:
            kwargs["fields"] = tuple(cast(Int, f)._value for f in fields._items)
        kwargs.update(_kwargs_from(int=int, version=version))
        # The native `bytes` and `int` names are shadowed by parameters
        # above; build the uuid lazily with what we have.
        self._impl = _uuid.UUID(**kwargs)

    @classmethod
    def _from_impl(cls, impl: _uuid.UUID) -> UUID:
        obj = cls.__new__(cls)
        obj._impl = impl
        return obj

    # Representations -------------------------------------------------

    @property
    def hex(self) -> Str:
        return Str(self._impl.hex)

    @property
    def urn(self) -> Str:
        return Str(self._impl.urn)

    @property
    def int(self) -> Int:
        return Int(self._impl.int)

    @property
    def bytes(self) -> Bytes:
        return Bytes(self._impl.bytes)

    @property
    def bytes_le(self) -> Bytes:
        return Bytes(self._impl.bytes_le)

    @property
    def fields(self) -> Tuple:
        return Tuple(*(Int(f) for f in self._impl.fields))

    # Individual field accessors --------------------------------------

    @property
    def time_low(self) -> Int:
        return Int(self._impl.time_low)

    @property
    def time_mid(self) -> Int:
        return Int(self._impl.time_mid)

    @property
    def time_hi_version(self) -> Int:
        return Int(self._impl.time_hi_version)

    @property
    def clock_seq_hi_variant(self) -> Int:
        return Int(self._impl.clock_seq_hi_variant)

    @property
    def clock_seq_low(self) -> Int:
        return Int(self._impl.clock_seq_low)

    @property
    def node(self) -> Int:
        return Int(self._impl.node)

    @property
    def time(self) -> Int:
        return Int(self._impl.time)

    @property
    def clock_seq(self) -> Int:
        return Int(self._impl.clock_seq)

    # Classification --------------------------------------------------

    @property
    def version(self) -> Int:
        # version can be None for unknown variants; CPython returns None.
        v = self._impl.version
        return Int(v if v is not None else 0)

    @property
    def variant(self) -> Str:
        return Str(self._impl.variant)

    @property
    def is_safe(self) -> Str:
        # SafeUUID enum → POOP flattens to a Str token (sanctioned
        # divergence: avoids introducing a one-off enum type).
        return Str(self._impl.is_safe.name.lower())

    # Representation --------------------------------------------------

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


UUID.__module__ = "builtins"
UUID.__name__ = "uuid"


class Uuid:
    """Namespace mirroring Python's `uuid` module.

    Generator entry points (`uuid1`/`3`/`4`/`5`/`6`/`7`/`8`), the
    `getnode()` helper, the standard namespace UUID constants, and
    the two sentinel UUIDs (`NIL`, `MAX`). The `UUID` class itself is
    bound alongside the namespace (PascalCase), mirroring CPython's
    `uuid.UUID`.
    """

    UUID: ClassVar[type[UUID]] = UUID

    # Standard namespace UUIDs (RFC 4122) as POOP UUID values.
    NAMESPACE_DNS: ClassVar[UUID] = UUID._from_impl(_uuid.NAMESPACE_DNS)
    NAMESPACE_URL: ClassVar[UUID] = UUID._from_impl(_uuid.NAMESPACE_URL)
    NAMESPACE_OID: ClassVar[UUID] = UUID._from_impl(_uuid.NAMESPACE_OID)
    NAMESPACE_X500: ClassVar[UUID] = UUID._from_impl(_uuid.NAMESPACE_X500)

    # Sentinel UUIDs.
    NIL: ClassVar[UUID] = UUID._from_impl(_uuid.NIL)
    MAX: ClassVar[UUID] = UUID._from_impl(_uuid.MAX)

    # Variant constants (Str tokens; CPython exposes plain str literals).
    RESERVED_NCS: ClassVar[Str] = Str(_uuid.RESERVED_NCS)
    RFC_4122: ClassVar[Str] = Str(_uuid.RFC_4122)
    RESERVED_MICROSOFT: ClassVar[Str] = Str(_uuid.RESERVED_MICROSOFT)
    RESERVED_FUTURE: ClassVar[Str] = Str(_uuid.RESERVED_FUTURE)

    # Generators ------------------------------------------------------

    @staticmethod
    def uuid1(node: Int | None = None, clock_seq: Int | None = None) -> UUID:
        return UUID._from_impl(
            _uuid.uuid1(
                None if node is None else node._value,
                None if clock_seq is None else clock_seq._value,
            )
        )

    @staticmethod
    def uuid3(namespace: UUID, name: Str) -> UUID:
        return UUID._from_impl(_uuid.uuid3(namespace._impl, name._value))

    @staticmethod
    def uuid4() -> UUID:
        return UUID._from_impl(_uuid.uuid4())

    @staticmethod
    def uuid5(namespace: UUID, name: Str) -> UUID:
        return UUID._from_impl(_uuid.uuid5(namespace._impl, name._value))

    @staticmethod
    def uuid6(node: Int | None = None, clock_seq: Int | None = None) -> UUID:
        return UUID._from_impl(
            _uuid.uuid6(
                None if node is None else node._value,
                None if clock_seq is None else clock_seq._value,
            )
        )

    @staticmethod
    def uuid7() -> UUID:
        return UUID._from_impl(_uuid.uuid7())

    @staticmethod
    def uuid8(
        a: Int | None = None,
        b: Int | None = None,
        c: Int | None = None,
    ) -> UUID:
        return UUID._from_impl(
            _uuid.uuid8(
                None if a is None else a._value,
                None if b is None else b._value,
                None if c is None else c._value,
            )
        )

    @staticmethod
    def getnode() -> Int:
        return Int(_uuid.getnode())
