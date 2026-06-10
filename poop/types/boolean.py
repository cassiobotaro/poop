from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, final

from poop.types.object import Object

if TYPE_CHECKING:
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
