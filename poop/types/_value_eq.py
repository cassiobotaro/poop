from typing import TYPE_CHECKING, ClassVar

from poop.types._mixin import _Mixin
from poop.types.boolean import false, to_boolean

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class _ValueEqMixin(_Mixin):  # noqa: PLW1641 — each concrete class hashes by value or not at all
    __slots__ = ()  # empty, as `_Mixin` says every mixin's must be

    _eq_attr: ClassVar[str]
    # Wrappers sharing a non-None _eq_group compare equal by value across the
    # group, even when they are different classes — mirroring CPython, where
    # ``set == frozenset`` and ``bytes == bytearray`` are True by value.
    _eq_group: ClassVar[str | None] = None

    def _eq_comparable(self, other: object) -> bool:
        # Either way round: CPython calls the *right* operand's `__eq__` first
        # when its class is a subclass of the left's, so a program's `class
        # Name(str)` compared against a `Str` ran this with the base on the
        # other side, answered `false` — not `NotImplemented` — and that was
        # final. `Name("a") == "a"` was `False` both ways and a dict keyed by
        # one was never found by the other, where CPython answers by value.
        if isinstance(other, type(self)) or isinstance(self, type(other)):
            return True
        group = self._eq_group
        return group is not None and group == getattr(other, "_eq_group", None)

    def __eq__(self, other: object) -> Boolean:
        if self._eq_comparable(other):
            attr = self._eq_attr
            return to_boolean(getattr(self, attr) == getattr(other, attr))
        return false
