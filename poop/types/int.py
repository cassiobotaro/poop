from typing import TYPE_CHECKING, Any, ClassVar, Literal, cast

from poop.types._numeric_compare import _NOT_NUMERIC, _num_value
from poop.types._unwrap import _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.complex import Complex
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
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


class Int(_ValueEqMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: _int | Int) -> None:
        self._value = value._value if isinstance(value, Int) else value

    def negated(self) -> Int:
        return Int(-self._value)

    def bit_invert(self) -> Int:
        return Int(~self._value)

    def max(self, other: Int) -> Int:
        return self if self._value >= other._value else other

    def min(self, other: Int) -> Int:
        return self if self._value <= other._value else other

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

    def to_bytes(self, length: Int, byteorder: Str) -> Bytes:
        from poop.types.bytes import Bytes

        return Bytes(
            self._value.to_bytes(
                length._value, cast(Literal["little", "big"], byteorder._value)
            )
        )

    @classmethod
    def from_bytes(cls, b: Bytes, byteorder: Str) -> Int:
        return cls(
            _int.from_bytes(b._value, cast(Literal["little", "big"], byteorder._value))
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
        self, other: Int | Float | Complex, modulus: Int | NoneClass | None = None
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
            raise TypeError(
                "pow() 3rd argument not allowed unless all arguments are integers"
            )
        return Int(pow(self._value, other._value, modulus._value))

    def pow(
        self, other: Int, modulus: Int | NoneClass | None = None
    ) -> Int | Float | Complex:
        return self.__pow__(other, modulus)

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
            raise TypeError(
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

    def __ceil__(self) -> Int:
        return self

    def __floor__(self) -> Int:
        return self

    def __trunc__(self) -> Int:
        return self

    def __round__(self, ndigits: Int | NoneClass | None = None) -> Int:

        n = _unwrap(ndigits, None)
        return Int(round(self._value, n))

    def round(self, ndigits: Int | NoneClass | None = None) -> Int:
        return self.__round__(ndigits)

    def __lt__(self, other: object) -> Boolean:
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._value < v)

    def __le__(self, other: object) -> Boolean:
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return NotImplemented
        return to_boolean(self._value <= v)

    def __gt__(self, other: object) -> Boolean:
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return NotImplemented
        return to_boolean(self._value > v)

    def __ge__(self, other: object) -> Boolean:
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return NotImplemented
        return to_boolean(self._value >= v)

    def __eq__(self, other: object) -> Boolean:
        # Boolean folds in as 1/0 — bool is an int subclass in CPython.
        # Complex joins the tower too: `1 == (1+0j)` is True in CPython.
        if isinstance(other, Complex):
            return to_boolean(self._value == other._value)
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return false
        return to_boolean(self._value == v)

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, Complex):
            return false if self._value == other._value else true
        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return true
        return false if self._value == v else true

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

    def __bool__(self) -> bool:
        return self._value != 0

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


Int.__module__ = "builtins"
Int.__name__ = "int"
