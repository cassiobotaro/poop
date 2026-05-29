from __future__ import annotations

import enum as _enum
from typing import Any, ClassVar

from poop.types.boolean import Boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def _wrap_value(value: Any) -> Any:
    if isinstance(value, bool):
        from poop.types.boolean import to_boolean

        return to_boolean(value)
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, str):
        return Str(value)
    return value


def _unwrap_for_lookup(value: Any) -> Any:
    # Used in _missing_ so `Color(Int(1))` finds the member with raw 1.
    if isinstance(value, Int | Float | Str):
        return value._value
    if isinstance(value, Boolean):
        return bool(value)
    return value


class _PoopEnumMixin:
    """Adds POOP-style helpers (`name_str`, `value_object`, `iter`) and
    POOP value lookup via `_missing_`.

    `.name` itself stays as a Python `str` — Python's `enum` machinery
    (including `@unique`) relies on raw-string identity, so overriding
    the descriptor breaks introspection. Use `.name_str` when you want
    a POOP `Str`.
    """

    _name_: str
    _value_: Any

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        unwrapped = _unwrap_for_lookup(value)
        if unwrapped is not value:
            return cls(unwrapped)  # ty: ignore[too-many-positional-arguments]
        # Defer to the parent's _missing_ (e.g. Flag/IntFlag's
        # bit-combination logic).
        return super()._missing_(value)  # ty: ignore[unresolved-attribute]

    def name_str(self) -> Str:
        return Str(self._name_)

    def value_object(self) -> Any:
        return _wrap_value(self._value_)

    @classmethod
    def iter(cls) -> List:
        return List(*cls)  # ty: ignore[not-iterable]


class Enum(_PoopEnumMixin, _enum.Enum):
    """POOP-flavoured `Enum` base — mirrors Python's `enum.Enum`.

    Members are class-side singletons (`Color.RED`, `Color(1)`).
    Lookups accept POOP `Int`/`Str` values: `Color(Int(1))` resolves
    to `Color.RED` exactly like `Color(1)` does. `.name` returns
    Python `str` (matching Python's Enum protocol); `.name_str()`
    returns a POOP `Str`. `.value` returns whatever the user assigned
    (POOP types pass through; raw Python primitives stay raw — wrap
    with `.value_object()` for an Int/Str/Float/Boolean).
    """


class IntEnum(_PoopEnumMixin, _enum.IntEnum):
    """Mirror of Python's `enum.IntEnum` — members are also `int`s."""


class StrEnum(_PoopEnumMixin, _enum.StrEnum):
    """Mirror of Python's `enum.StrEnum` — members are also `str`s."""


class Flag(_PoopEnumMixin, _enum.Flag):
    """Mirror of Python's `enum.Flag` — bitwise-combinable members."""


class IntFlag(_PoopEnumMixin, _enum.IntFlag):
    """Mirror of Python's `enum.IntFlag` — int-valued combinable flags."""


# `enum.ReprEnum` cannot be subclassed without a data-type mixin, so
# expose it directly. POOP users compose it like CPython does:
# `class Color(int, ReprEnum): ...`.
ReprEnum = _enum.ReprEnum


def auto() -> Any:
    """Mirror of Python's `enum.auto()` — sequential value generator
    for use inside an `Enum` class body.
    """
    return _enum.auto()


class EnumNamespace:
    """Namespace mirroring Python's `enum` module.

    Bases (`Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, `ReprEnum`)
    are also exposed bare alongside this namespace. `auto()` generates
    sequential member values; the decorators (`unique`, `verify`,
    `member`, `nonmember`) apply to Enum classes.

    `EnumType` metaclass access is out of scope — POOP forbids
    introspection.
    """

    Enum: ClassVar[type[Enum]] = Enum
    IntEnum: ClassVar[type[IntEnum]] = IntEnum
    StrEnum: ClassVar[type[StrEnum]] = StrEnum
    Flag: ClassVar[type[Flag]] = Flag
    IntFlag: ClassVar[type[IntFlag]] = IntFlag
    ReprEnum: ClassVar[type[ReprEnum]] = ReprEnum

    auto: ClassVar[Any] = staticmethod(auto)

    unique: ClassVar[Any] = staticmethod(_enum.unique)
    verify: ClassVar[Any] = staticmethod(_enum.verify)
    member: ClassVar[Any] = staticmethod(_enum.member)
    nonmember: ClassVar[Any] = staticmethod(_enum.nonmember)
    global_enum: ClassVar[Any] = staticmethod(_enum.global_enum)
    pickle_by_enum_name: ClassVar[Any] = staticmethod(_enum.pickle_by_enum_name)
    pickle_by_global_name: ClassVar[Any] = staticmethod(_enum.pickle_by_global_name)
    property: ClassVar[Any] = _enum.property  # enum-specific @property descriptor

    # Flag.boundary policies.
    STRICT: ClassVar[Any] = _enum.STRICT
    CONFORM: ClassVar[Any] = _enum.CONFORM
    EJECT: ClassVar[Any] = _enum.EJECT
    KEEP: ClassVar[Any] = _enum.KEEP

    # `verify` policies.
    CONTINUOUS: ClassVar[Any] = _enum.CONTINUOUS
    NAMED_FLAGS: ClassVar[Any] = _enum.NAMED_FLAGS
    UNIQUE: ClassVar[Any] = _enum.UNIQUE
