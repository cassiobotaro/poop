from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, final

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.complex import Complex
    from poop.types.float import Float
    from poop.types.int import Int
    from poop.types.none import NoneClass


class Boolean(Object, ABC):
    """Abstract base for Smalltalk-style boolean objects."""

    __slots__ = ()

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
    def __and__(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def __or__(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def __bool__(self) -> bool: ...

    @abstractmethod
    def __str__(self) -> str: ...

    def __lt__(self, other: Boolean) -> Boolean:
        return to_boolean(bool(self) < bool(other))

    def __le__(self, other: Boolean) -> Boolean:
        return to_boolean(bool(self) <= bool(other))

    def __gt__(self, other: Boolean) -> Boolean:
        return to_boolean(bool(self) > bool(other))

    def __ge__(self, other: Boolean) -> Boolean:
        return to_boolean(bool(self) >= bool(other))

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

    def _num(self, other: object) -> Any:
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

    def __pow__(self, other: object, modulus: Any = None) -> Int | Float | Complex:
        return self._as_int().__pow__(self._num(other), modulus)

    def __rpow__(self, other: object) -> Any:
        return self._rev(other, "__pow__")


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

    def __and__(self, other: Boolean) -> Boolean:
        return other

    def __or__(self, other: Boolean) -> Boolean:
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

    def __and__(self, other: Boolean) -> Boolean:
        return self

    def __or__(self, other: Boolean) -> Boolean:
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


Boolean.__module__ = "builtins"
Boolean.__name__ = "bool"

# The singleton classes answer "bool" too — class_name() and error
# messages read type(true).__name__, not the abstract base's.
_TrueClass.__module__ = "builtins"
_TrueClass.__name__ = "bool"
_FalseClass.__module__ = "builtins"
_FalseClass.__name__ = "bool"
