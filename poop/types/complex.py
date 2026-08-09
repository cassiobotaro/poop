from types import NotImplementedType
from typing import TYPE_CHECKING

from poop.types._cloak import cloak
from poop.types._message import binary_refusal
from poop.types.boolean import Boolean, false, to_boolean, true
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.float import Float

_complex = complex  # alias to avoid shadowing by Complex class name


class Complex(Object):
    __slots__ = ("_value",)

    def __init__(self, value: _complex | Complex) -> None:
        self._value = value._value if isinstance(value, Complex) else value

    def real(self) -> Float:
        from poop.types.float import Float

        return Float(self._value.real)

    def imag(self) -> Float:
        from poop.types.float import Float

        return Float(self._value.imag)

    def conjugate(self) -> Complex:
        return Complex(self._value.conjugate())

    def __abs__(self) -> Float:
        from poop.types.float import Float

        return Float(abs(self._value))

    def abs(self) -> Float:
        return self.__abs__()

    def _coerce(self, other: object) -> _complex | None:
        from poop.types.float import Float
        from poop.types.int import Int

        if isinstance(other, Complex):
            return other._value
        if isinstance(other, (Int, Float)):
            return _complex(other._value)
        # `bool` is an `int` subclass, so a Boolean folds in as 1/0 across the
        # numeric tower — `True + (1+2j)`, `(1+2j) ** True`, etc. all coerce.
        if isinstance(other, Boolean):
            return _complex(bool(other))
        return None

    def __add__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(self._value + v)

    def __radd__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(v + self._value)

    def __sub__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(self._value - v)

    def __rsub__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(v - self._value)

    def __mul__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(self._value * v)

    def __rmul__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(v * self._value)

    def __truediv__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(self._value / v)

    def __rtruediv__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(v / self._value)

    def __pow__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(self._value**v)

    def __rpow__(self, other: object) -> Complex | NotImplementedType:
        v = self._coerce(other)
        if v is None:
            return NotImplemented
        return Complex(v**self._value)

    def pow(self, other: object) -> Complex:
        # `no_pow` names `a.pow(b)` as the substitute for the builtin, and
        # `Complex` wrapped `__abs__` and `__neg__` as `abs()` and `negated()`
        # but never this one — so `complex(1, 1) ** 2` computed and
        # `complex(1, 1).pow(2)` answered `complex does not understand #pow`.
        result = self.__pow__(other)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                binary_refusal("complex", "pow", type(other).__name__)
            )
        return result

    def negated(self) -> Complex:
        return Complex(-self._value)

    def __neg__(self) -> Complex:
        return self.negated()

    # Equality bridges to the rest of the numeric tower, mirroring CPython,
    # where ``complex(1, 0) == 1`` and ``complex(1, 0) == True`` are True.
    def __eq__(self, other: object) -> Boolean:
        v = self._coerce(other)
        return false if v is None else to_boolean(self._value == v)

    def __ne__(self, other: object) -> Boolean:
        v = self._coerce(other)
        return true if v is None else to_boolean(self._value != v)

    def __hash__(self) -> int:
        return hash(self._value)

    def __bool__(self) -> bool:
        # `bool(0j)` is False in CPython; without this, Complex would
        # inherit Object's default (always-truthy) and answer True for
        # zero, corrupting `not_()`, `assert_()`, and conditionals.
        return self._value != 0

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


cloak(Complex, "complex")
