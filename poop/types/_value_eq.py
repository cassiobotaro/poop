from typing import TYPE_CHECKING, ClassVar

from poop.types.boolean import false, true

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class _ValueEqMixin:
    _eq_attr: ClassVar[str]

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, type(self)):
            attr = self._eq_attr
            return true if getattr(self, attr) == getattr(other, attr) else false
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, type(self)):
            attr = self._eq_attr
            return false if getattr(self, attr) == getattr(other, attr) else true
        return true
