import builtins as _builtins
from typing import TYPE_CHECKING, Any, Literal, cast

from poop.types._cloak import cloak
from poop.types._numeric_compare import (
    _NOT_NUMERIC,
    _num_value,
    _NumericCompareMixin,
)
from poop.types._unwrap import _faithful, _unwrap
from poop.types.boolean import true
from poop.types.complex import Complex
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.float import Float
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_int = int  # alias to avoid shadowing by Int.int() method

_NOT_INTEGRAL: Any = object()


def _integral_value(other: object) -> Any:
    """Raw int behind an Int/Boolean operand, else the ``_NOT_INTEGRAL`` sentinel.

    Bitwise and shift operators accept only integral operands: ``Int`` and
    ``Boolean`` (``bool`` is an ``int`` subclass, so ``5 & True == 1``). A
    ``Float`` or a foreign operand yields the sentinel, so the caller returns
    ``NotImplemented`` and CPython raises its faithful ``TypeError`` instead of
    leaking an ``AttributeError`` from a missing ``other._value``.
    """
    from poop.types.boolean import Boolean

    if isinstance(other, Int):
        return other._value
    if isinstance(other, Boolean):
        return 1 if other else 0
    return _NOT_INTEGRAL


class Int(_NumericCompareMixin, Object):
    __slots__ = ("_value",)

    def __init__(self, value: _int | Int) -> None:
        self._value = value._value if isinstance(value, Int) else value

    def negated(self) -> Int:
        return Int(-self._value)

    def bit_invert(self) -> Int:
        return Int(~self._value)

    # Compare the operands themselves rather than reading `other._value`:
    # the numeric mixin folds a Boolean to 1/0 (`(1).min(True)` works, as
    # `bool` is an `int` subclass in CPython) and answers NotImplemented for a
    # foreign operand, so CPython raises the faithful comparison TypeError
    # instead of leaking #_value through does_not_understand. Wrapping in a
    # tuple keeps the no-`others` case answering self, unlike `max(x)`.
    # The cast mirrors typeshed, where `bool` is a subtype of `int` and
    # `max(0, True)` is typed `int` though it answers `True`.
    def max(self, *others: Int | Boolean) -> Int:
        return cast("Int", _builtins.max((self, *others)))

    def min(self, *others: Int | Boolean) -> Int:
        return cast("Int", _builtins.min((self, *others)))

    def bit_count(self) -> Int:
        return Int(self._value.bit_count())

    def bit_length(self) -> Int:
        return Int(self._value.bit_length())

    def is_integer(self) -> Boolean:
        return true

    @property
    def real(self) -> Int:
        return self

    @property
    def imag(self) -> Int:
        return Int(0)

    @property
    def numerator(self) -> Int:
        return self

    @property
    def denominator(self) -> Int:
        return Int(1)

    def conjugate(self) -> Int:
        return self

    def as_integer_ratio(self) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(self, Int(1))

    def to_bytes(
        self,
        length: Int | NoneClass | None = None,
        byteorder: Str | NoneClass | None = None,
        *,
        signed: Boolean | NoneClass | None = None,
    ) -> Bytes:
        from poop.types._unwrap import _opt_int, _unwrap_bool
        from poop.types.bytes import Bytes

        return Bytes(
            self._value.to_bytes(
                _opt_int(length, 1),
                cast(Literal["little", "big"], _unwrap(byteorder, "big")),
                signed=_unwrap_bool(signed, False),
            )
        )

    @classmethod
    def from_bytes(
        cls,
        b: Bytes,
        byteorder: Str | NoneClass | None = None,
        *,
        signed: Boolean | NoneClass | None = None,
    ) -> Int:
        from poop.types._unwrap import _unwrap_bool

        return cls(
            _int.from_bytes(
                _faithful(b),
                cast(Literal["little", "big"], _unwrap(byteorder, "big")),
                signed=_unwrap_bool(signed, False),
            )
        )

    def __abs__(self) -> Int:
        return Int(abs(self._value))

    def abs(self) -> Int:
        return self.__abs__()

    def __add__(self, other: object) -> Int | Float:
        from poop.types.float import Float

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__radd__ run
        if isinstance(other, Float):
            return Float(self._value + other._value)
        return Int(self._value + other._value)

    def __sub__(self, other: object) -> Int | Float:
        from poop.types.float import Float

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rsub__ run
        if isinstance(other, Float):
            return Float(self._value - other._value)
        return Int(self._value - other._value)

    def __mul__(self, other: object) -> Int | Float:
        from poop.types.float import Float

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rmul__ run (Str/Bytes repeat, etc.)
        if isinstance(other, Float):
            return Float(self._value * other._value)
        return Int(self._value * other._value)

    def __truediv__(self, other: object) -> Float:
        from poop.types.float import Float

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rtruediv__ run
        return Float(self._value / other._value)

    def __floordiv__(self, other: object) -> Int | Float:
        from poop.types.float import Float

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rfloordiv__ run
        if isinstance(other, Float):
            return Float(self._value // other._value)
        return Int(self._value // other._value)

    def __mod__(self, other: object) -> Int | Float:
        from poop.types.float import Float

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rmod__ run
        if isinstance(other, Float):
            return Float(self._value % other._value)
        return Int(self._value % other._value)

    def __pow__(
        self, other: object, modulus: Int | NoneClass | None = None
    ) -> Int | Float | Complex:
        from poop.types._unwrap import _is_absent
        from poop.types.float import Float

        if isinstance(other, Complex):
            return NotImplemented
        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rpow__ run (e.g. Boolean)
        if _is_absent(modulus):
            result = self._value**other._value
            if isinstance(result, complex):
                return Complex(result)
            if isinstance(result, float):
                return Float(result)
            return Int(result)
        if isinstance(other, Float):
            raise MIRRORS["TypeError"](
                "pow() 3rd argument not allowed unless all arguments are integers"
            )
        return Int(pow(self._value, other._value, _faithful(modulus)))

    def pow(
        self, other: object, modulus: Int | NoneClass | None = None
    ) -> Int | Float | Complex:
        result = self.__pow__(other, modulus)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                f"unsupported operand type(s) for ** or pow(): "
                f"'int' and '{type(other).__name__}'"
            )
        return result

    def __divmod__(self, other: object) -> Tuple:
        from poop.types.float import Float
        from poop.types.tuple import Tuple

        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return NotImplemented  # let other.__rdivmod__ run / faithful TypeError
        q, r = divmod(self._value, v)
        if isinstance(other, Float):
            return Tuple(Float(q), Float(r))
        return Tuple(Int(q), Int(r))

    def divmod(self, other: object) -> Tuple:
        result = self.__divmod__(other)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                f"unsupported operand type(s) for divmod(): "
                f"'int' and '{type(other).__name__}'"
            )
        return result

    def __lshift__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(self._value << v)

    def __rshift__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(self._value >> v)

    def __and__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(self._value & v)

    def __or__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(self._value | v)

    def __xor__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(self._value ^ v)

    # Reflected bitwise/shift operators — CPython's int defines these too, so a
    # `<integral> OP Int` expression (e.g. `True << 5`, where Boolean has no
    # `__lshift__`) resolves here instead of leaking a TypeError.
    def __rlshift__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(v << self._value)

    def __rrshift__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(v >> self._value)

    def __rand__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(v & self._value)

    def __ror__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(v | self._value)

    def __rxor__(self, other: object) -> Int:
        v = _integral_value(other)
        if v is _NOT_INTEGRAL:
            return NotImplemented
        return Int(v ^ self._value)

    def __ceil__(self) -> Int:
        return self

    def ceil(self) -> Int:
        return self.__ceil__()

    def __floor__(self) -> Int:
        return self

    def floor(self) -> Int:
        return self.__floor__()

    def __trunc__(self) -> Int:
        return self

    def trunc(self) -> Int:
        return self.__trunc__()

    def __round__(self, ndigits: Int | NoneClass | None = None) -> Int:

        n = _unwrap(ndigits, None)
        return Int(round(self._value, n))

    def round(self, ndigits: Int | NoneClass | None = None) -> Int:
        return self.__round__(ndigits)

    # Ordering (__lt__/__le__/__gt__/__ge__) and equality (__eq__/__ne__)
    # across the numeric tower live in _NumericCompareMixin, driven by
    # _order_value() below (Int's raw value is self._value, the default).

    def __hash__(self) -> _int:
        return hash(self._value)

    def bin(self) -> Str:
        from poop.types.string import Str

        return Str(bin(self._value))

    def hex(self) -> Str:
        from poop.types.string import Str

        return Str(hex(self._value))

    def oct(self) -> Str:
        from poop.types.string import Str

        return Str(oct(self._value))

    def chr(self) -> Str:
        from poop.types.string import Str

        return Str(chr(self._value))

    def __int__(self) -> _int:
        return self._value

    def __index__(self) -> _int:
        # Python's index protocol, so an `Int` *is* an index: `xs.at(i)` hands
        # the wrapper straight to CPython instead of unwrapping `i._value` by
        # hand, which leaked `#_value` for a foreign index and refused a
        # Boolean one. Answering a native is required — CPython demands an
        # `int` here, like `__len__` and `__bool__`.
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


cloak(Int, "int")
