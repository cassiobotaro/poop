from typing import TYPE_CHECKING

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.float import Float

_complex = complex  # alias to avoid shadowing by Complex class name


class Complex(Object):
    __slots__ = ("_value",)

    def __init__(self, value: _complex) -> None:
        self._value = value

    @property
    def real(self) -> Float:
        from poop.types.float import Float

        return Float(self._value.real)

    @property
    def imag(self) -> Float:
        from poop.types.float import Float

        return Float(self._value.imag)

    def conjugate(self) -> Complex:
        return Complex(self._value.conjugate())

    def abs(self) -> Float:
        from poop.types.float import Float

        return Float(abs(self._value))

    def __abs__(self) -> Float:
        return self.abs()

    def _coerce(self, other: object) -> _complex | None:
        from poop.types.float import Float
        from poop.types.int import Int

        if isinstance(other, Complex):
            return other._value
        if isinstance(other, (Int, Float)):
            return _complex(other._value)
        return None

    def __add__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(self._value + v)

    def __radd__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(v + self._value)

    def __sub__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(self._value - v)

    def __rsub__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(v - self._value)

    def __mul__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(self._value * v)

    def __rmul__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(v * self._value)

    def __truediv__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(self._value / v)

    def __rtruediv__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(v / self._value)

    def __pow__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(self._value**v)

    def __rpow__(self, other: object) -> Complex:
        v = self._coerce(other)
        if v is None:
            return NotImplemented  # type: ignore[return-value]
        return Complex(v**self._value)

    def negated(self) -> Complex:
        return Complex(-self._value)

    def __neg__(self) -> Complex:
        return Complex(-self._value)

    def __pos__(self) -> Complex:
        return Complex(self._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Complex):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Complex):
            return false if self._value == other._value else true
        return true

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__
