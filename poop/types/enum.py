from __future__ import annotations

import enum as _enum
from typing import Any, ClassVar

from poop.types._bridge import to_poop, to_python
from poop.types.boolean import Boolean, to_boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


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
        return to_poop(self._value_)

    @classmethod
    def iter(cls) -> List:
        return List(*cls)  # ty: ignore[not-iterable]

    # Operator bridging — members answer POOP values so the one branching
    # idiom (`(state == State.IDLE).if_true(...)`) works. Boolean preserves
    # truthiness, so the enum machinery (alias resolution, dict lookup via
    # __hash__) keeps working.

    def __eq__(self, other: object) -> Boolean:
        result = super().__eq__(other)
        if result is NotImplemented:
            return to_boolean(self is other)
        return to_boolean(result)

    def __ne__(self, other: object) -> Boolean:
        result = super().__ne__(other)
        if result is NotImplemented:
            return to_boolean(self is not other)
        return to_boolean(result)

    def __hash__(self) -> int:
        return super().__hash__()

    def __lt__(self, other: Any) -> Any:
        result = super().__lt__(other)  # ty: ignore[unresolved-attribute]
        return result if result is NotImplemented else to_boolean(result)

    def __le__(self, other: Any) -> Any:
        result = super().__le__(other)  # ty: ignore[unresolved-attribute]
        return result if result is NotImplemented else to_boolean(result)

    def __gt__(self, other: Any) -> Any:
        result = super().__gt__(other)  # ty: ignore[unresolved-attribute]
        return result if result is NotImplemented else to_boolean(result)

    def __ge__(self, other: Any) -> Any:
        result = super().__ge__(other)  # ty: ignore[unresolved-attribute]
        return result if result is NotImplemented else to_boolean(result)


class _IntEnumArithmeticMixin:
    """Routes IntEnum arithmetic (raw `int` in CPython) through to_poop so
    `Priority.LOW + Priority.HIGH` answers a POOP `Int`. Operands are
    unwrapped via `to_python` (POOP `Int`/`Float` or another member)."""

    __slots__ = ()

    _value_: Any

    def __add__(self, other: Any) -> Any:
        return to_poop(self._value_ + to_python(other))

    def __radd__(self, other: Any) -> Any:
        return to_poop(to_python(other) + self._value_)

    def __sub__(self, other: Any) -> Any:
        return to_poop(self._value_ - to_python(other))

    def __rsub__(self, other: Any) -> Any:
        return to_poop(to_python(other) - self._value_)

    def __mul__(self, other: Any) -> Any:
        return to_poop(self._value_ * to_python(other))

    def __rmul__(self, other: Any) -> Any:
        return to_poop(to_python(other) * self._value_)

    def __floordiv__(self, other: Any) -> Any:
        return to_poop(self._value_ // to_python(other))

    def __mod__(self, other: Any) -> Any:
        return to_poop(self._value_ % to_python(other))

    def __pow__(self, other: Any) -> Any:
        return to_poop(self._value_ ** to_python(other))

    def __truediv__(self, other: Any) -> Any:
        return to_poop(self._value_ / to_python(other))


_NOT_GIVEN: Any = object()


class _PoopEnumMeta(_enum.EnumType):
    """Metaclass intercepting the functional API (`Enum("Color", names)`).

    CPython's `EnumType.__call__` receives the POOP `Str`/`List`/`Dict`
    arguments and tries to unpack them, failing in three different ways.
    When the functional form is used (a `names` argument is present),
    unwrap every argument via `to_python` before delegating; the bare
    lookup form (`Color(Int(1))`) is left untouched so `_missing_` runs
    (CPython distinguishes the two via a `_not_given` sentinel, so the
    `names` argument must be omitted entirely for the lookup path).
    """

    def __call__(
        cls, value: Any, names: Any = _NOT_GIVEN, *args: Any, **kwargs: Any
    ) -> Any:
        if names is _NOT_GIVEN:
            return super().__call__(value, **kwargs)
        return super().__call__(
            to_python(value),
            to_python(names),
            *(to_python(a) for a in args),
            **{k: to_python(v) for k, v in kwargs.items()},
        )


class Enum(_PoopEnumMixin, _enum.Enum, metaclass=_PoopEnumMeta):
    """POOP-flavoured `Enum` base — mirrors Python's `enum.Enum`.

    Members are class-side singletons (`Color.RED`, `Color(1)`).
    Lookups accept POOP `Int`/`Str` values: `Color(Int(1))` resolves
    to `Color.RED` exactly like `Color(1)` does. `.name` returns
    Python `str` (matching Python's Enum protocol); `.name_str()`
    returns a POOP `Str`. `.value` returns whatever the user assigned
    (POOP types pass through; raw Python primitives stay raw — wrap
    with `.value_object()` for an Int/Str/Float/Boolean); `auto()`
    members answer a POOP `Int` like a literal member.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[Any]
    ) -> Any:
        # `auto()` would otherwise leave a raw `int` in `.value`, unlike a
        # literal member (rewritten to a POOP `Int` by the transformer). Run
        # CPython's incrementing generator over unwrapped prior values, then
        # re-wrap so `Color.RED.value` answers a POOP `Int`. Defined here on
        # the base rather than the mixin because the enum machinery copies
        # `_generate_next_value_` from the raw enum parent, bypassing a mixin.
        # The primitive-mixed kinds (IntEnum/IntFlag/StrEnum) and Flag keep the
        # raw generator on purpose — see their class docstrings.
        raw = _enum.Enum._generate_next_value_(
            name, start, count, [to_python(v) for v in last_values]
        )
        return to_poop(raw)


class IntEnum(
    _PoopEnumMixin, _IntEnumArithmeticMixin, _enum.IntEnum, metaclass=_PoopEnumMeta
):
    """Mirror of Python's `enum.IntEnum` — members are also `int`s.

    `auto()` is left to CPython's raw generator: an `IntEnum` member *is* an
    `int`, so `.value` is a raw `int` like a literal member (use
    `.value_object()` for a POOP `Int`). Wrapping would be both inconsistent
    with literals and rejected by the `int`-mixed constructor.
    """


class StrEnum(_PoopEnumMixin, _enum.StrEnum, metaclass=_PoopEnumMeta):
    """Mirror of Python's `enum.StrEnum` — members are also `str`s.

    `auto()` (the lower-cased member name) is left raw: a `StrEnum` member *is*
    a `str`, and a POOP `Str` is not a `str` subclass so the `str`-mixed
    constructor would reject it. `.value` is a raw `str` like a literal member;
    use `.value_object()` for a POOP `Str`.
    """


class Flag(_PoopEnumMixin, _enum.Flag, metaclass=_PoopEnumMeta):
    """Mirror of Python's `enum.Flag` — bitwise-combinable members.

    `auto()` is left to CPython's raw generator: Flag's mask/combination
    machinery (`READ | EXEC`) operates on raw `int` values, so wrapping would
    break it. Use `.value_object()` for a POOP `Int`.
    """


class IntFlag(
    _PoopEnumMixin, _IntEnumArithmeticMixin, _enum.IntFlag, metaclass=_PoopEnumMeta
):
    """Mirror of Python's `enum.IntFlag` — int-valued combinable flags.

    Bitwise `|`/`&`/`^`/`~` keep CPython's flag-combination semantics
    (they answer flag members); only plain arithmetic (`+`/`-`/…) is
    bridged to POOP `Int`. As with `IntEnum`, `auto()` stays a raw `int`
    (use `.value_object()` for a POOP `Int`).
    """


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
