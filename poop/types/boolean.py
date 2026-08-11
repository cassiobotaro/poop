import builtins as _builtins
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast, final

from poop.types._cloak import cloak
from poop.types._numeric_compare import _NumericCompareMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.bytes import Bytes
    from poop.types.complex import Complex
    from poop.types.float import Float
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple


class Boolean(_NumericCompareMixin, Object, ABC):
    """Abstract base for Smalltalk-style boolean objects."""

    __slots__ = ()

    # `bool` is an `int` subclass, so a Boolean folds to 1/0 for the numeric
    # tower's comparison protocol (ordering + equality) shared via
    # _NumericCompareMixin — `true > Float(0.5)` and `true == Int(1)` are true.
    def _order_value(self) -> int:
        return int(bool(self))

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def if_true[T](self, block: Callable[[], T]) -> T | NoneClass: ...

    @abstractmethod
    def if_false[T](self, block: Callable[[], T]) -> T | NoneClass: ...

    @abstractmethod
    def if_true_if_false[T](
        self,
        true_block: Callable[[], T],
        false_block: Callable[[], T],
    ) -> T: ...

    @abstractmethod
    def if_false_if_true[T](
        self,
        false_block: Callable[[], T],
        true_block: Callable[[], T],
    ) -> T: ...

    @abstractmethod
    def and_(self, block: Callable[[], Boolean]) -> Boolean: ...

    @abstractmethod
    def or_(self, block: Callable[[], Boolean]) -> Boolean: ...

    @abstractmethod
    def not_(self) -> Boolean: ...

    @abstractmethod
    def xor(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def eqv(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def _bool_and(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def _bool_or(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def __bool__(self) -> bool: ...

    @abstractmethod
    def __str__(self) -> str: ...

    def __index__(self) -> int:
        # Same reason `_order_value` folds to 1/0: `bool` is an `int` subclass,
        # so CPython indexes with it — `[1, 2][True]` is 2, `"ab"[True]` is
        # "b". Without this the whole Boolean rung was unusable as an index.
        return 1 if self else 0

    # Ordering (__lt__/__le__/__gt__/__ge__) and equality (__eq__/__ne__)
    # against the numeric tower live in _NumericCompareMixin; _order_value()
    # above folds a Boolean to 1/0 so it compares as `bool`'s int subclass does.

    # Arithmetic — `bool` is an `int` subclass in CPython, so a Boolean acts
    # as 1/0 in numeric expressions (`True + 1 == 2`, `sum([True, True]) == 2`).
    # POOP's numeric tower defines no reflected dunders (each forward operator
    # accepts the types it knows), so Boolean carries both halves itself: the
    # forward ops fold self — and a Boolean operand — to Int and delegate to
    # Int's arithmetic; the reflected ops compute ``other <op> int(self)`` so
    # ``3 - True`` reuses ``Int.__sub__``.
    def _as_int(self) -> Int:
        from poop.types.int import Int

        return Int(1) if self else Int(0)

    # The int-side *messages*, delegated through the same fold the operators
    # use. Everything that makes `bool` an `int` in CPython was re-supplied by
    # hand — arithmetic, reflected arithmetic, comparison across the tower,
    # `__index__` — and the messages were not, so a program told to stop
    # writing `abs(flag)` had nowhere to go: `no_abs` names `x.abs()`,
    # `no_divmod` names `a.divmod(b)`, `no_bin` names `x.bin()`, and none of
    # them existed here. Each answers what CPython answers, which is an `Int`
    # (`abs(True)` is `1`, not `True`) — answering a `Boolean` would be a quiet
    # type error. Written out rather than generated: a loop over a name list
    # would be shorter but would defeat `ty`, `dir()` and `:methods`.
    def abs(self) -> Int:
        return self._as_int().abs()

    def bit_length(self) -> Int:
        return self._as_int().bit_length()

    def bit_count(self) -> Int:
        return self._as_int().bit_count()

    def bit_invert(self) -> Int:
        return self._as_int().bit_invert()

    def negated(self) -> Int:
        return self._as_int().negated()

    def divmod(self, other: object) -> Tuple:
        return self._as_int().divmod(self._num(other))

    def pow(
        self, other: object, modulus: Int | NoneClass | None = None
    ) -> Int | Float | Complex:
        return self._as_int().pow(self._num(other), modulus)

    def round(self, ndigits: Int | NoneClass | None = None) -> Int:
        return self._as_int().round(ndigits)

    def ceil(self) -> Int:
        return self._as_int().ceil()

    def floor(self) -> Int:
        return self._as_int().floor()

    def trunc(self) -> Int:
        return self._as_int().trunc()

    def bin(self) -> Str:
        return self._as_int().bin()

    def hex(self) -> Str:
        return self._as_int().hex()

    def oct(self) -> Str:
        return self._as_int().oct()

    def chr(self) -> Str:
        return self._as_int().chr()

    def to_bytes(
        self,
        length: Int | NoneClass | None = None,
        byteorder: Str | NoneClass | None = None,
        *,
        signed: Boolean | NoneClass | None = None,
    ) -> Bytes:
        return self._as_int().to_bytes(length, byteorder, signed=signed)

    @classmethod
    def from_bytes(
        cls,
        b: Bytes,
        byteorder: Str | NoneClass | None = None,
        *,
        signed: Boolean | NoneClass | None = None,
    ) -> Boolean:
        """`to_bytes` read back, the half of the pair that was missing.

        The only int-side message with no instance to fold, so it cannot go
        through `_as_int` like the rest of the family — it delegates to
        `Int.from_bytes` and folds the answer. Its absence was sharper than a
        plain gap: the near-miss hint pointed at `#to_bytes`, telling the
        reader that the message they did not want is the one that exists.

        A `Boolean` and not an `Int`, unlike `abs` and its neighbours: CPython
        runs this one through `cls`, so `bool.from_bytes(b"\\x05", "big")` is
        `True` — the answer is the receiver's kind here, not the fold's.
        """
        from poop.types.int import Int

        return to_boolean(bool(Int.from_bytes(b, byteorder, signed=signed)))

    def format(self, spec: Str | NoneClass | None = None) -> Str:
        # `bool(self)`, not `_as_int()`, unlike every message around it:
        # `format(True, "")` is `'True'` and `format(1, "")` is `'1'`, so
        # folding first would change `True.format()` — the one spelling that
        # worked — from `True` to `1`. `Object.format` reads `_value`, which a
        # Boolean has no slot for, so it fell through to `object.__format__`
        # and refused every non-empty spec while `"{:>6}".format(True)`, which
        # routes through `to_python`, answered `'     1'`.
        from poop.types._argument import text_like
        from poop.types._unwrap import _is_absent
        from poop.types.string import Str

        # Through `text_like` for the reason `Object.format` does it: a
        # non-`Str` spec answered `format() argument 2 must be str, not int`.
        raw = "" if _is_absent(spec) else text_like(spec, "format", "a str")
        return Str(_builtins.format(bool(self), raw))

    def as_integer_ratio(self) -> Tuple:
        return self._as_int().as_integer_ratio()

    def is_integer(self) -> Boolean:
        return self._as_int().is_integer()

    def real(self) -> Int:
        return self._as_int().real()

    def imag(self) -> Int:
        return self._as_int().imag()

    def numerator(self) -> Int:
        return self._as_int().numerator()

    def denominator(self) -> Int:
        return self._as_int().denominator()

    def conjugate(self) -> Int:
        return self._as_int().conjugate()

    # Not through `_as_int`, unlike every message above: `min`/`max` answer one
    # of their *operands*, and CPython's `min(True, 5)` is `True`. Folding
    # first would answer `1` for a receiver the program still holds as a flag.
    def max(
        self,
        *others: Int | Boolean,
        key: Callable[[Any], Any] | NoneClass | None = None,
    ) -> Int | Boolean:
        from poop.types._minmax import _MISSING, _minmax

        return cast(
            "Int | Boolean",
            _minmax(_builtins.max, "#max", (self, *others), key, _MISSING),
        )

    def min(
        self,
        *others: Int | Boolean,
        key: Callable[[Any], Any] | NoneClass | None = None,
    ) -> Int | Boolean:
        from poop.types._minmax import _MISSING, _minmax

        return cast(
            "Int | Boolean",
            _minmax(_builtins.min, "#min", (self, *others), key, _MISSING),
        )

    def _num(self, other: object) -> object:
        return other._as_int() if isinstance(other, Boolean) else other

    def _rev(self, other: object, op: str) -> Any:
        method = getattr(other, op, None)
        if method is None:
            return NotImplemented
        return method(self._as_int())

    def __add__(self, other: object) -> Int | Float:
        return self._as_int().__add__(self._num(other))

    def __radd__(self, other: object) -> Any:
        return self._rev(other, "__add__")

    def __sub__(self, other: object) -> Int | Float:
        return self._as_int().__sub__(self._num(other))

    def __rsub__(self, other: object) -> Any:
        return self._rev(other, "__sub__")

    def __mul__(self, other: object) -> Int | Float:
        return self._as_int().__mul__(self._num(other))

    def __rmul__(self, other: object) -> Any:
        return self._rev(other, "__mul__")

    def __truediv__(self, other: object) -> Float:
        return self._as_int().__truediv__(self._num(other))

    def __rtruediv__(self, other: object) -> Any:
        return self._rev(other, "__truediv__")

    def __floordiv__(self, other: object) -> Int | Float:
        return self._as_int().__floordiv__(self._num(other))

    def __rfloordiv__(self, other: object) -> Any:
        return self._rev(other, "__floordiv__")

    def __mod__(self, other: object) -> Int | Float:
        return self._as_int().__mod__(self._num(other))

    def __rmod__(self, other: object) -> Any:
        return self._rev(other, "__mod__")

    def __pow__(
        self, other: object, modulus: Int | NoneClass | None = None
    ) -> Int | Float | Complex:
        return self._as_int().__pow__(self._num(other), modulus)

    def __rpow__(self, other: object) -> Any:
        return self._rev(other, "__pow__")

    # Bitwise — `bool` is an `int` subclass, so `&`, `|` and `^` stay in
    # boolean algebra only between two Booleans (`True & False is False`);
    # against an `Int` they fold to 1/0 and yield an `Int` (`True & 5 == 1`,
    # `True ^ 5 == 4`), exactly as CPython does. Int operands delegate to
    # Int's bitwise dunders, so the result is a POOP wrapper, not a raw int.
    def __and__(self, other: object) -> Boolean | Int:
        if isinstance(other, Boolean):
            return self._bool_and(other)
        return self._as_int().__and__(other)

    def __rand__(self, other: object) -> Any:
        return self._rev(other, "__and__")

    def __or__(self, other: object) -> Boolean | Int:
        if isinstance(other, Boolean):
            return self._bool_or(other)
        return self._as_int().__or__(other)

    def __ror__(self, other: object) -> Any:
        return self._rev(other, "__or__")

    def __xor__(self, other: object) -> Boolean | Int:
        if isinstance(other, Boolean):
            return self.xor(other)
        return self._as_int().__xor__(other)

    def __rxor__(self, other: object) -> Any:
        return self._rev(other, "__xor__")

    # Shifts, unlike the three above, have no boolean-algebra reading — there
    # is no Boolean answer to give, so they fold to `Int` whatever the other
    # operand is, as CPython does (`True << True` is `2`). Without them the
    # mixed cases still worked, because `Int` answers them from its own side
    # (`__rlshift__` says so), and only `Boolean << Boolean` reached neither.
    def __lshift__(self, other: object) -> Int:
        return self._as_int().__lshift__(self._num(other))

    def __rlshift__(self, other: object) -> Any:
        return self._rev(other, "__lshift__")

    def __rshift__(self, other: object) -> Int:
        return self._as_int().__rshift__(self._num(other))

    def __rrshift__(self, other: object) -> Any:
        return self._rev(other, "__rshift__")


@final
class _TrueClass(Boolean):
    __slots__ = ()

    def if_true[T](self, block: Callable[[], T]) -> T:
        return block()

    def if_false[T](self, block: Callable[[], T]) -> NoneClass:
        from poop.types.none import none

        return none

    def if_true_if_false[T](
        self,
        true_block: Callable[[], T],
        false_block: Callable[[], T],
    ) -> T:
        return true_block()

    def if_false_if_true[T](
        self,
        false_block: Callable[[], T],
        true_block: Callable[[], T],
    ) -> T:
        return true_block()

    def and_(self, block: Callable[[], Boolean]) -> Boolean:
        return block()

    def or_(self, block: Callable[[], Boolean]) -> Boolean:
        return self

    def not_(self) -> Boolean:
        return false

    def xor(self, other: Boolean) -> Boolean:
        return other.not_()

    def eqv(self, other: Boolean) -> Boolean:
        return other

    def _bool_and(self, other: Boolean) -> Boolean:
        return other

    def _bool_or(self, other: Boolean) -> Boolean:
        return self

    def __bool__(self) -> bool:
        return True

    def __str__(self) -> str:
        return "True"

    def __hash__(self) -> int:
        return hash(True)


@final
class _FalseClass(Boolean):
    __slots__ = ()

    def if_true[T](self, block: Callable[[], T]) -> NoneClass:
        from poop.types.none import none

        return none

    def if_false[T](self, block: Callable[[], T]) -> T:
        return block()

    def if_true_if_false[T](
        self,
        true_block: Callable[[], T],
        false_block: Callable[[], T],
    ) -> T:
        return false_block()

    def if_false_if_true[T](
        self,
        false_block: Callable[[], T],
        true_block: Callable[[], T],
    ) -> T:
        return false_block()

    def and_(self, block: Callable[[], Boolean]) -> Boolean:
        return self

    def or_(self, block: Callable[[], Boolean]) -> Boolean:
        return block()

    def not_(self) -> Boolean:
        return true

    def xor(self, other: Boolean) -> Boolean:
        return other

    def eqv(self, other: Boolean) -> Boolean:
        return other.not_()

    def _bool_and(self, other: Boolean) -> Boolean:
        return self

    def _bool_or(self, other: Boolean) -> Boolean:
        return other

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return "False"

    def __hash__(self) -> int:
        return hash(False)


true: Boolean = _TrueClass()
false: Boolean = _FalseClass()


def to_boolean(value: object) -> Boolean:
    """Map any Python truth value onto the POOP `Boolean` singletons."""
    return true if value else false


cloak(Boolean, "bool")

# The singleton classes answer "bool" too — class_name() and error
# messages read type(true).__name__, not the abstract base's.
cloak(_TrueClass, "bool")
cloak(_FalseClass, "bool")
