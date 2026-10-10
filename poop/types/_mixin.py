"""The one base of the shared mixins — the plain classes outside the `Object` tree.

Two things every mixin used to restate. An empty `__slots__`, because a
slot-less class anywhere in an MRO restores the per-instance `__dict__` for
everything below it: one mixin alone defeated the declaration on 36 of the 49
wrappers, so a `Str` accepted attached state and two equal `Str`s could carry
different attributes. The empty tuple cannot collide with a concrete class's
own slots, which is what makes it safe on all of them — and each mixin still
has to write it, since a subclass without the declaration grows a `__dict__`
of its own whatever its base declared; what lives here once is the reason.

And a cloak as `object`, the root's own spelling: a mixin's methods are
inherited by many wrappers, so no single builtin name is true for all of them
— and left alone CPython blamed `_IterableMixin` in every wrong-arity message,
a private name `_reject_private` exists to keep out of user code. The cloak is
part of a class's declaration, so it is a class keyword here as it is on the
wrappers: `class _BytesLikeMixin(_Mixin, name="bytes")` for the one mixin whose
two receivers share a truer name.
"""

from poop.types._cloak import cloak
from poop.types.meta import PoopMeta


class _Mixin:
    __slots__ = ()

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: object) -> None:
        # A wrapper inheriting the mixin is a POOP class, and its cloak is
        # `Object.__init_subclass__`'s to apply: the keyword travels on up.
        if isinstance(cls, PoopMeta):
            kwargs["name"] = name
            super().__init_subclass__(**kwargs)
            return
        super().__init_subclass__(**kwargs)
        cloak(cls, name or "object")
