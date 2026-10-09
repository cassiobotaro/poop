import builtins
import math
import operator
from typing import TYPE_CHECKING, Literal, cast

from poop.types._alias import wrapped_instance
from poop.types._argument import Key, an_int, byte_order, byte_source
from poop.types._cloak import cloak
from poop.types._message import article, binary_refusal
from poop.types._minmax import _minmax
from poop.types._numeric_compare import (
    _num_value,
    _NumericCompareMixin,
)
from poop.types._pow import reflected_pow
from poop.types._raw import _faithful
from poop.types._sentinel import MISSING, NOT_INTEGRAL, NOT_NUMERIC, NotIntegral
from poop.types._unwrap import _is_absent, _unwrap_bool
from poop.types.boolean import Boolean, true
from poop.types.complex import Complex
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.bytes import Bytes
    from poop.types.float import Float
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple


def _integral_value(other: object) -> int | NotIntegral:
    """Raw int behind an Int/Boolean operand, else the ``NOT_INTEGRAL`` sentinel.

    Bitwise and shift operators accept only integral operands: ``Int`` and
    ``Boolean`` (``bool`` is an ``int`` subclass, so ``5 & True == 1``). A
    ``Float`` or a foreign operand yields the sentinel, so the caller returns
    ``NotImplemented`` and CPython raises its faithful ``TypeError`` instead of
    leaking an ``AttributeError`` from a missing ``other._value``.
    """
    if isinstance(other, Int):
        return other._value
    if isinstance(other, Boolean):
        return 1 if other else 0
    return NOT_INTEGRAL


class Int(_NumericCompareMixin, Object):
    __slots__ = ("_value",)

    def __init__(self, value: int | Int) -> None:
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
    # `Int | Boolean`, as `Boolean.max` already says: the answer is one of
    # the operands, and `(0).max(True)` answers `True`. A cast to `Int` used
    # to say otherwise, mirroring typeshed's `max(0, True)`.
    # `key` is keyword-only, as CPython spells it: a positional block would be
    # indistinguishable from one more operand, and that was the bug — the block
    # was compared as a value, so a *comparable* extra argument would have
    # answered a plausible wrong number in silence. `default` stays out; CPython
    # refuses it alongside multiple positional arguments too.
    def max(
        self,
        *others: Int | Boolean,
        key: Key[Int | Boolean] = None,
    ) -> Int | Boolean:
        return _minmax(builtins.max, "#max", (self, *others), key, MISSING)

    def min(
        self,
        *others: Int | Boolean,
        key: Key[Int | Boolean] = None,
    ) -> Int | Boolean:
        return _minmax(builtins.min, "#min", (self, *others), key, MISSING)

    def bit_count(self) -> Int:
        return Int(self._value.bit_count())

    def bit_length(self) -> Int:
        return Int(self._value.bit_length())

    def is_integer(self) -> Boolean:
        return true

    def real(self) -> Int:
        return self

    def imag(self) -> Int:
        return Int(0)

    def numerator(self) -> Int:
        return self

    def denominator(self) -> Int:
        return Int(1)

    def conjugate(self) -> Int:
        return self

    def as_integer_ratio(self) -> Tuple:
        # circular: tuple imports int
        from poop.types.tuple import Tuple  # noqa: PLC0415

        return Tuple(self, Int(1))

    def to_bytes(
        self,
        length: Int | NoneClass | None = None,
        byteorder: Str | NoneClass | None = None,
        *,
        signed: Boolean | NoneClass | None = None,
    ) -> Bytes:
        # circular: bytes imports int
        from poop.types.bytes import Bytes  # noqa: PLC0415

        return Bytes(
            self._value.to_bytes(
                an_int(length, "to_bytes", "length", 1),
                cast("Literal['little', 'big']", byte_order(byteorder, "to_bytes")),
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
        return wrapped_instance(
            cls,
            int.from_bytes(
                byte_source(b, "from_bytes"),
                cast("Literal['little', 'big']", byte_order(byteorder, "from_bytes")),
                signed=_unwrap_bool(signed, False),
            ),
        )

    def abs(self) -> Int:
        return Int(abs(self._value))

    __abs__ = abs

    def _arith(
        self, other: object, op: Callable[[int, int | float], int | float]
    ) -> Int | Float:
        """`self op other`, an `Int` beside an `Int` and a `Float` beside a `Float`.

        Written once and handed the operator, as `_OrderedMixin._compare` is.
        Anything outside the pair answers `NotImplemented`, so the operand's
        reflected method runs — `Str`/`Bytes` repeat for `*`, `Boolean` and
        `Complex` for the rest.
        """
        # circular: float imports int
        from poop.types.float import Float  # noqa: PLC0415

        if not isinstance(other, (Int, Float)):
            return NotImplemented
        # An `int` answer is an `Int`, a `float` one a `Float`, whichever
        # operator produced it. Branched here rather than through `to_poop`:
        # ty reads `int | float` as `float` and would answer `Float` alone.
        raw = op(self._value, other._value)
        return Int(raw) if isinstance(raw, int) else Float(raw)

    def __add__(self, other: object) -> Int | Float:
        return self._arith(other, operator.add)

    def __sub__(self, other: object) -> Int | Float:
        return self._arith(other, operator.sub)

    def __mul__(self, other: object) -> Int | Float:
        return self._arith(other, operator.mul)

    def __truediv__(self, other: object) -> Float:
        # `/` answers a `float` on every pair, so `_arith` answers a `Float`.
        return cast("Float", self._arith(other, operator.truediv))

    def __floordiv__(self, other: object) -> Int | Float:
        return self._arith(other, operator.floordiv)

    def __mod__(self, other: object) -> Int | Float:
        return self._arith(other, operator.mod)

    def __pow__(
        self, other: object, modulus: Int | NoneClass | None = None
    ) -> Int | Float | Complex:
        # circular: float imports int, and _bridge imports both
        from poop.types._bridge import to_poop  # noqa: PLC0415
        from poop.types.float import Float  # noqa: PLC0415

        if isinstance(other, Complex):
            return NotImplemented
        if not isinstance(other, (Int, Float)):
            return NotImplemented  # let other.__rpow__ run (e.g. Boolean)
        if _is_absent(modulus):
            return to_poop(self._value**other._value)
        if isinstance(other, Float):
            raise MIRRORS["TypeError"](
                "pow's modulus is only defined when both operands are ints"
            )
        # Guarded here because CPython's three-operand form names all three —
        # `unsupported operand type(s) for ** or pow(): 'int', 'int', 'str'` —
        # a shape no rewording of the binary message would reach.
        if not isinstance(modulus, Int):
            raise MIRRORS["TypeError"](
                f"pow's modulus must be an int, got {article(type(modulus).__name__)}"
            )
        # The third way a modulus can be wrong, and the one left to CPython:
        # `pow() 3rd argument cannot be 0` names the builtin `no_pow` forbids,
        # spelt as the call this message substitutes.
        if modulus._value == 0:
            raise MIRRORS["ValueError"]("pow's modulus cannot be 0")
        return Int(pow(self._value, other._value, _faithful(modulus)))

    def pow(self, other: object, modulus: Int | NoneClass | None = None) -> object:
        # The reflected half is part of the operation, not an extra: `__pow__`
        # answers `NotImplemented` for a `Complex` *on purpose*, so CPython's
        # operator protocol falls through to `Complex.__rpow__`. `2 ** 1+1j`
        # did exactly that while `(2).pow(complex(1, 1))` refused — the
        # substitute narrower than both the operator POOP still allows and the
        # builtin it replaces. `modulus` is guarded because the three-argument
        # form has no reflected counterpart in CPython either.
        result = self.__pow__(other, modulus)
        if result is NotImplemented:
            result = reflected_pow(self, other, modulus)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                binary_refusal("int", "pow", type(other).__name__)
            )
        return result

    def __divmod__(self, other: object) -> Tuple:
        # circular: float imports int
        from poop.types.float import Float  # noqa: PLC0415

        # circular: tuple imports int
        from poop.types.tuple import Tuple  # noqa: PLC0415

        v = _num_value(other)
        if v is NOT_NUMERIC:
            return NotImplemented  # let other.__rdivmod__ run / faithful TypeError
        # A `float` operand answers floats, as CPython's `divmod(7, 2.0)` does;
        # the `int` operand — an `Int`, or a `Boolean` folded to 1/0 — ints.
        if isinstance(v, float):
            return Tuple(*map(Float, divmod(self._value, v)))
        return Tuple(*map(Int, divmod(self._value, v)))

    def divmod(self, other: object) -> Tuple:
        result = self.__divmod__(other)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                binary_refusal("int", "divmod", type(other).__name__)
            )
        return result

    def _bitwise(
        self, other: object, op: Callable[[int, int], int], *, reflected: bool = False
    ) -> Int:
        """`self op other` for a shift or bitwise operator; `other op self`
        when `reflected`. An operand that is not integral answers
        `NotImplemented`.
        """
        v = _integral_value(other)
        if v is NOT_INTEGRAL:
            return NotImplemented
        return Int(op(v, self._value) if reflected else op(self._value, v))

    def __lshift__(self, other: object) -> Int:
        return self._bitwise(other, operator.lshift)

    def __rshift__(self, other: object) -> Int:
        return self._bitwise(other, operator.rshift)

    def __and__(self, other: object) -> Int:
        return self._bitwise(other, operator.and_)

    def __or__(self, other: object) -> Int:
        return self._bitwise(other, operator.or_)

    def __xor__(self, other: object) -> Int:
        return self._bitwise(other, operator.xor)

    # Reflected bitwise/shift operators — CPython's int defines these too, so a
    # `<integral> OP Int` expression (e.g. `True << 5`, where Boolean has no
    # `__lshift__`) resolves here instead of leaking a TypeError.
    def __rlshift__(self, other: object) -> Int:
        return self._bitwise(other, operator.lshift, reflected=True)

    def __rrshift__(self, other: object) -> Int:
        return self._bitwise(other, operator.rshift, reflected=True)

    # `&`, `|` and `^` commute, so their reflected halves are the operators.
    __rand__ = __and__
    __ror__ = __or__
    __rxor__ = __xor__

    def ceil(self) -> Int:
        return self

    __ceil__ = ceil

    def floor(self) -> Int:
        return self

    __floor__ = floor

    def trunc(self) -> Int:
        return self

    __trunc__ = trunc

    def round(self, ndigits: Int | NoneClass | None = None) -> Int:
        n = an_int(ndigits, "round", "ndigits", None)
        return Int(round(self._value, n))

    __round__ = round

    # Ordering (__lt__/__le__/__gt__/__ge__) and equality (__eq__/__ne__)
    # across the numeric tower live in _NumericCompareMixin, driven by
    # _order_value() below.
    def _order_value(self) -> int:
        return self._value

    def __hash__(self) -> int:
        return hash(self._value)

    def bin(self) -> Str:
        # circular: string imports int
        from poop.types.string import Str  # noqa: PLC0415

        return Str(bin(self._value))

    def hex(self) -> Str:
        # circular: string imports int
        from poop.types.string import Str  # noqa: PLC0415

        return Str(hex(self._value))

    def oct(self) -> Str:
        # circular: string imports int
        from poop.types.string import Str  # noqa: PLC0415

        return Str(oct(self._value))

    def chr(self) -> Str:
        # circular: string imports int
        from poop.types.string import Str  # noqa: PLC0415

        try:
            return Str(chr(self._value))
        except ValueError:
            # CPython answers `chr() arg not in range(0x110000)` — the builtin
            # `no_chr` forbids, spelled as a call, with the bound in hex.
            raise MIRRORS["ValueError"](
                f"{self._value} is not a character code — codes run from 0 to 1114111"
            ) from None

    # Python 3.15 moved the integer functions out of `math` into
    # `math.integer` (PEP 791) because their only receiver is an integer —
    # which is the argument for their being messages here, as `ceil` and
    # `floor` already are. All six, as CPython has them; Smalltalk's `Integer`
    # answers four of them (`gcd:`, `lcm:`, `factorial`, `sqrtFloor`). The
    # `math` names still reach the same functions, and are what `ty` knows.
    def _non_negative(self, selector: str) -> int:
        if self._value < 0:
            # CPython: `isqrt() argument must be nonnegative`, `factorial()
            # not defined for negative values`, `n must be a non-negative
            # integer` — the message as a call, or an argument name the
            # program never wrote.
            raise MIRRORS["ValueError"](
                f"#{selector} needs a non-negative receiver, got {self._value}"
            )
        return self._value

    def isqrt(self) -> Int:
        return Int(math.isqrt(self._non_negative("isqrt")))

    def factorial(self) -> Int:
        return Int(math.factorial(self._non_negative("factorial")))

    def gcd(self, *others: Int) -> Int:
        return Int(
            math.gcd(self._value, *(an_int(o, "gcd", "operand") for o in others))
        )

    def lcm(self, *others: Int) -> Int:
        return Int(
            math.lcm(self._value, *(an_int(o, "lcm", "operand") for o in others))
        )

    def _draws(self, k: object, selector: str) -> int:
        count = an_int(k, selector, "k")
        if count < 0:
            raise MIRRORS["ValueError"](
                f"#{selector}'s k must be non-negative, got {count}"
            )
        return count

    def comb(self, k: Int) -> Int:
        return Int(math.comb(self._non_negative("comb"), self._draws(k, "comb")))

    def perm(self, k: Int | NoneClass | None = None) -> Int:
        n = self._non_negative("perm")
        if _is_absent(k):
            return Int(math.perm(n))
        return Int(math.perm(n, self._draws(k, "perm")))

    def __int__(self) -> int:
        return self._value

    def __index__(self) -> int:
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
