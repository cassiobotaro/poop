from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Object:
    __slots__ = ()

    def is_none(self) -> Boolean:
        from poop.types.boolean import false

        return false

    def not_none(self) -> Boolean:
        from poop.types.boolean import true

        return true

    def not_(self) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self) else true

    def class_name(self) -> str:
        return type(self).__name__

    def responds_to(self, symbol: str) -> Boolean:
        from poop.types.boolean import false, true

        return true if hasattr(self, symbol) else false

    def __str__(self) -> str:
        return f"<{self.class_name()}>"

    def __repr__(self) -> str:
        return str(self)
