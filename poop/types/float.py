import builtins
import math
import operator
from typing import TYPE_CHECKING

from poop.types import mirrors
from poop.types._alias import wrapped_instance
from poop.types._argument import Key, a_number, an_int, text_like
from poop.types._message import answered
from poop.types._minmax import _minmax
from poop.types._numeric_compare import (
    _num_value,
    _NumericCompareMixin,
)
from poop.types._pow import reflected_pow
from poop.types._sentinel import MISSING, NOT_NUMERIC
from poop.types._unwrap import _is_absent
from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple

# circular: _bridge imports float
lazy from poop.types._bridge import to_poop

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean
    from poop.types.complex import Complex
    from poop.types.none import NoneClass


class Float(_NumericCompareMixin, Object, name="float"):
    __slots__ = ("_value",)

    def __init__(self, value: float | Float) -> None:
        self._value = value._value if isinstance(value, Float) else float(value)

    def negated(self) -> Float:
        return Float(-self._value)

    # Same reasoning as `Int.max` / `Int.min`: comparing the operands routes
    # a Boolean through the numeric mixin and a foreign operand to CPython's
    # faithful TypeError, instead of reading `other._value` and leaking it.
    # The answer is one of the operands, whichever rung of the tower it sits
    # on — `(1.5).max(2)` answers `2`, an `Int` — which a cast to `Float`
    # used to deny, mirroring typeshed.
    # `key` is keyword-only, as CPython spells it: a positional block would be
    # indistinguishable from one more operand, which is how it used to be read.
    def max(
        self,
        *others: Float | Int | Boolean,
        key: Key[Float | Int | Boolean] = None,
    ) -> Float | Int | Boolean:
        return _minmax(builtins.max, "#max", (self, *others), key, MISSING)

    def min(
        self,
        *others: Float | Int | Boolean,
        key: Key[Float | Int | Boolean] = None,
    ) -> Float | Int | Boolean:
        return _minmax(builtins.min, "#min", (self, *others), key, MISSING)

    def is_integer(self) -> Boolean:
        return to_boolean(self._value.is_integer())

    # The `math` predicates whose only receiver is a float, as `Int` answers
    # the `math.integer` six: CPython's names, `math`'s answers. Three are
    # Python 3.15's (`isnormal`, `issubnormal`, `signbit`); `isnan`, `isinf`
    # and `isfinite` are the same decision — INFECTIONS.md, Float.
    def isnan(self) -> Boolean:
        return to_boolean(math.isnan(self._value))

    def isinf(self) -> Boolean:
        return to_boolean(math.isinf(self._value))

    def isfinite(self) -> Boolean:
        return to_boolean(math.isfinite(self._value))

    def isnormal(self) -> Boolean:
        return to_boolean(math.isnormal(self._value))

    def issubnormal(self) -> Boolean:
        return to_boolean(math.issubnormal(self._value))

    def signbit(self) -> Boolean:
        return to_boolean(math.signbit(self._value))

    def as_integer_ratio(self) -> Tuple:
        n, d = self._value.as_integer_ratio()
        return Tuple(Int(n), Int(d))

    def conjugate(self) -> Float:
        return self

    def hex(self) -> Str:
        # `float(...)` for the checker alone: `__init__` already normalised the
        # slot, but a `float` annotation admits `int`, which has no `hex`.
        return Str(float(self._value).hex())

    @classmethod
    def fromhex(cls, s: Str) -> Float:
        # `bad argument type for built-in operation` names neither the
        # receiver, the message nor the argument. The two byte twins already
        # answered `#fromhex expects a str, got an int`.
        return wrapped_instance(
            cls, float.fromhex(text_like(s, "fromhex", "a str", (str,)))
        )

    @classmethod
    def from_number(cls, x: Int | Float | Boolean) -> Float:
        """Python 3.14's `float.from_number`: a number, and only a number.

        `float(x)` also reads text; this is the constructor that refuses it.
        Through `wrapped_instance`, as `fromhex` is, so `class Money(float)`
        answers a `Money` as CPython's does.
        """
        return wrapped_instance(cls, float(a_number(x, "from_number", real=True)))

    def real(self) -> Float:
        return self

    def imag(self) -> Float:
        return Float(0.0)

    def abs(self) -> Float:
        return Float(abs(self._value))

    __abs__ = abs

    def _arith(self, other: object, op: Callable[[float, int | float], float]) -> Float:
        """`self op other` against an `Int` or a `Float`.

        Anything else answers `NotImplemented`, so the operand's reflected
        method runs.
        """
        if not isinstance(other, (Int, Float)):
            return NotImplemented
        return Float(op(self._value, other._value))

    def __add__(self, other: object) -> Float:
        return self._arith(other, operator.add)

    def __sub__(self, other: object) -> Float:
        return self._arith(other, operator.sub)

    def __mul__(self, other: object) -> Float:
        return self._arith(other, operator.mul)

    def __truediv__(self, other: object) -> Float:
        return self._arith(other, operator.truediv)

    def __floordiv__(self, other: object) -> Float:
        return self._arith(other, operator.floordiv)

    def __mod__(self, other: object) -> Float:
        return self._arith(other, operator.mod)

    def __pow__(self, other: object) -> Float | Complex:
        if not isinstance(other, (Int, Float)):
            return NotImplemented  # let other.__rpow__ run (Boolean, Complex)
        return to_poop(self._value**other._value)

    def pow(self, other: object, modulus: Int | NoneClass | None = None) -> object:
        # The third slot exists so the message has the same shape on every
        # rung: without it `(2.0).pow(3, 5)` answered CPython's *signature*
        # error — `float.pow() takes 2 positional arguments but 3 were given`,
        # naming a message as a call — while `(2).pow(3.0, 5)` one line away
        # answered the operation. CPython refuses the float form too, but as
        # an operation, so the refusal is `Int.__pow__`'s own sentence.
        #
        # In `pow`, not `__pow__`: the operator never carries a third operand
        # (`a ** b % m` is two operations, and the builtin `pow` is banned).
        if not _is_absent(modulus):
            raise mirrors.TypeError(
                "pow's modulus is only defined when both operands are ints"
            )
        # See `Int.pow`: `__pow__` answers `NotImplemented` for a `Complex` so
        # the operator can fall through to `Complex.__rpow__`, and the message
        # has to complete the same protocol or it refuses what `**` computes.
        result = self.__pow__(other)
        if result is NotImplemented:
            result = reflected_pow(self, other, None)
        return answered(result, "float", "pow", other)

    def __divmod__(self, other: object) -> Tuple:
        v = _num_value(other)
        if v is NOT_NUMERIC:
            return NotImplemented  # let other.__rdivmod__ run / faithful TypeError
        q, r = divmod(self._value, v)
        return Tuple(Float(q), Float(r))

    def divmod(self, other: object) -> Tuple:
        return answered(self.__divmod__(other), "float", "divmod", other)

    def ceil(self) -> Int:
        return Int(math.ceil(self._value))

    __ceil__ = ceil

    def floor(self) -> Int:
        return Int(math.floor(self._value))

    __floor__ = floor

    def trunc(self) -> Int:
        return Int(math.trunc(self._value))

    __trunc__ = trunc

    def round(self, ndigits: Int | NoneClass | None = None) -> Int | Float:
        # An `Int` without `ndigits`, a `Float` with one, as CPython's `round`
        # answers — branched on the answer rather than on the argument, which
        # is also what keeps ty from reading the pair as a `Float` alone.
        raw = round(self._value, an_int(ndigits, "round", "ndigits", None))
        return Int(raw) if isinstance(raw, int) else Float(raw)

    __round__ = round

    def __int__(self) -> int:
        return int(self._value)

    # Ordering (__lt__/__le__/__gt__/__ge__) and equality (__eq__) across
    # the numeric tower live in _NumericCompareMixin, driven by _order_value()
    # below. __ne__ is Object's, flipping whatever __eq__ answers.
    def _order_value(self) -> float:
        return self._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __float__(self) -> float:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0.0

    def __str__(self) -> str:
        return str(self._value)
