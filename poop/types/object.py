from builtins import print as _builtins_print
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.error import Error
    from poop.types.int import Int
    from poop.types.string import Str


class Object:
    __slots__ = ()

    def if_none(self, block: Callable[[], Any]) -> Object:
        return self

    def if_not_none[T](self, block: Callable[[Object], T]) -> T:
        return block(self)

    def is_none(self) -> Boolean:
        from poop.types.boolean import false

        return false

    def not_none(self) -> Boolean:
        from poop.types.boolean import true

        return true

    def not_(self) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self) else true

    def class_name(self) -> Str:
        from poop.types.string import Str

        return Str(type(self).__name__)

    def hash(self) -> Int:
        from poop.types.int import Int

        return Int(hash(self))

    def id(self) -> Int:
        from poop.types.int import Int

        return Int(id(self))

    def callable(self) -> Boolean:
        import builtins

        from poop.types.boolean import false, true

        return true if builtins.callable(self) else false

    def is_instance(self, type_: type) -> Boolean:
        from poop.types.boolean import false, true

        return true if isinstance(self, type_) else false

    def has_attr(self, symbol: str) -> Boolean:
        from poop.types.boolean import false, true

        return true if hasattr(self, symbol) else false

    def on_error(
        self,
        block: Callable[[], Any],
        exc_type: type[BaseException],
        handler: Callable[[Error], Any],
    ) -> Any:
        from poop.types.error import Error

        try:
            return block()
        except exc_type as e:
            return handler(Error(e))

    def print(self, end: str = "\n", flush: bool = False) -> Object:
        _builtins_print(str(self), end=end, flush=flush)  # noqa: T201
        return self

    def __str__(self) -> str:
        return f"<{self.class_name()}>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return true if self is other else false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __hash__(self) -> int:
        return id(self)
