from typing import TYPE_CHECKING, ClassVar

from poop.types.boolean import false, to_boolean, true

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class _ValueEqMixin:
    _eq_attr: ClassVar[str]
    # Wrappers sharing a non-None _eq_group compare equal by value across the
    # group, even when they are different classes — mirroring CPython, where
    # ``set == frozenset`` and ``bytes == bytearray`` are True by value.
    _eq_group: ClassVar[str | None] = None

    def _eq_comparable(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return True
        group = self._eq_group
        return group is not None and group == getattr(other, "_eq_group", None)

    def __eq__(self, other: object) -> Boolean:
        if self._eq_comparable(other):
            attr = self._eq_attr
            return to_boolean(getattr(self, attr) == getattr(other, attr))
        return false

    def __ne__(self, other: object) -> Boolean:
        if self._eq_comparable(other):
            attr = self._eq_attr
            return false if getattr(self, attr) == getattr(other, attr) else true
        return true
