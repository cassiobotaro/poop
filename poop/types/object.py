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

    def is_identical(self, other: Object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def not_identical(self, other: Object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def not_(self) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self) else true

    def assert_(self, message: Str | NoneClass | None = None) -> Object:
        from poop.types._unwrap import _is_absent

        if bool(self):
            return self
        if _is_absent(message):
            raise AssertionError
        raise AssertionError(message._value)

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
        from poop.types.boolean import to_boolean

        return to_boolean(builtins.callable(self))

    def is_instance(self, type_: type) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(isinstance(self, type_))

    @classmethod
    def is_subclass(cls, other: type) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(issubclass(cls, other))

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

    def format(self, spec: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap
        from poop.types.string import Str

        spec_value = _unwrap(spec, "")
        target = builtins.getattr(self, "_value", self)
        return Str(builtins.format(target, spec_value))

    def get_attr(self, name: Str, *default: Any) -> Any:
        return builtins.getattr(self, name._value, *default)

    def has_attr(self, symbol: Str) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(hasattr(self, symbol._value))

    def set_attr(self, name: Str, value: Any) -> NoneClass:
        from poop.types.none import none

        builtins.setattr(self, name._value, value)
        return none

    def del_attr(self, name: Str) -> NoneClass:
        from poop.types.none import none

        builtins.delattr(self, name._value)
        return none

    def print(
        self,
        end: Str | NoneClass | None = None,
        flush: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        from poop.types._unwrap import _unwrap, _unwrap_bool
        from poop.types.none import none

        end_value = _unwrap(end, "\n")
        flush_value = _unwrap_bool(flush, False)
        _builtins_print(str(self), end=end_value, flush=flush_value)  # noqa: T201
        return none

    def __str__(self) -> str:
        return f"<{self.class_name()}>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __hash__(self) -> int:
        return id(self)


Object.__module__ = "builtins"
Object.__name__ = "object"
