import builtins
from builtins import print as _builtins_print
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
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
        from poop.types.boolean import false, true

        return true if builtins.callable(self) else false

    def is_instance(self, type_: type) -> Boolean:
        from poop.types.boolean import false, true

        return true if isinstance(self, type_) else false

    @classmethod
    def is_subclass(cls, other: type) -> Boolean:
        from poop.types.boolean import false, true

        return true if issubclass(cls, other) else false

    def repr(self) -> Str:
        from poop.types.string import Str

        return Str(builtins.repr(self))

    def ascii(self) -> Str:
        from poop.types.string import Str

        return Str(builtins.ascii(self))

    def dir(self) -> List:
        from poop.types.list import List
        from poop.types.string import Str

        return List(*(Str(name) for name in builtins.dir(self)))

    def format(self, spec: Str | None = None) -> Str:
        from poop.types.string import Str

        spec_value = "" if spec is None else spec._value
        target = builtins.getattr(self, "_value", self)
        return Str(builtins.format(target, spec_value))

    def get_attr(self, name: str, *default: Any) -> Any:
        return builtins.getattr(self, name, *default)

    def has_attr(self, symbol: str) -> Boolean:
        from poop.types.boolean import false, true

        return true if hasattr(self, symbol) else false

    def set_attr(self, name: str, value: Any) -> NoneClass:
        from poop.types.none import none

        builtins.setattr(self, name, value)
        return none

    def del_attr(self, name: str) -> NoneClass:
        from poop.types.none import none

        builtins.delattr(self, name)
        return none

    def print(self, end: str = "\n", flush: bool = False) -> None:
        _builtins_print(str(self), end=end, flush=flush)  # noqa: T201

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
