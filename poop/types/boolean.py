from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, final

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class Boolean(Object, ABC):
    """Abstract base for Smalltalk-style boolean objects."""

    __slots__ = ()

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def if_true[T](self, block: Callable[[], T]) -> T | None: ...

    @abstractmethod
    def if_false[T](self, block: Callable[[], T]) -> T | None: ...

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
    def while_true(
        self,
        cond_block: Callable[[], Boolean],
        body_block: Callable[[], Any],
    ) -> NoneClass: ...

    @abstractmethod
    def while_false(
        self,
        cond_block: Callable[[], Boolean],
        body_block: Callable[[], Any],
    ) -> NoneClass: ...

    @abstractmethod
    def assert_(self, message: object = "") -> Boolean: ...

    @abstractmethod
    def __and__(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def __or__(self, other: Boolean) -> Boolean: ...

    @abstractmethod
    def __bool__(self) -> bool: ...

    @abstractmethod
    def __str__(self) -> str: ...


@final
class _TrueClass(Boolean):
    __slots__ = ()

    def if_true[T](self, block: Callable[[], T]) -> T:
        return block()

    def if_false[T](self, block: Callable[[], T]) -> None:
        return None

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

    def assert_(self, message: object = "") -> Boolean:
        return self

    def __and__(self, other: Boolean) -> Boolean:
        return other

    def __or__(self, other: Boolean) -> Boolean:
        return self

    def while_true(
        self,
        cond_block: Callable[[], Boolean],
        body_block: Callable[[], Any],
    ) -> NoneClass:
        from poop.types.none import none

        while bool(cond_block()):
            body_block()
        return none

    def while_false(
        self,
        cond_block: Callable[[], Boolean],
        body_block: Callable[[], Any],
    ) -> NoneClass:
        from poop.types.none import none

        while not bool(cond_block()):
            body_block()
        return none

    def __bool__(self) -> bool:
        return True

    def __str__(self) -> str:
        return "True"

    def __hash__(self) -> int:
        return hash(True)


@final
class _FalseClass(Boolean):
    __slots__ = ()

    def if_true[T](self, block: Callable[[], T]) -> None:
        return None

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

    def assert_(self, message: object = "") -> Boolean:
        raise AssertionError(str(message))

    def __and__(self, other: Boolean) -> Boolean:
        return self

    def __or__(self, other: Boolean) -> Boolean:
        return other

    def while_true(
        self,
        cond_block: Callable[[], Boolean],
        body_block: Callable[[], Any],
    ) -> NoneClass:
        from poop.types.none import none

        while bool(cond_block()):
            body_block()
        return none

    def while_false(
        self,
        cond_block: Callable[[], Boolean],
        body_block: Callable[[], Any],
    ) -> NoneClass:
        from poop.types.none import none

        while not bool(cond_block()):
            body_block()
        return none

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return "False"

    def __hash__(self) -> int:
        return hash(False)


true: Boolean = _TrueClass()
false: Boolean = _FalseClass()
