"""The class side of POOP — classes are objects and answer messages.

Smalltalk's "everything is an object" includes classes: `Foo name`, `Foo
superclass` are ordinary messages to an ordinary object. Without this, POOP's
thesis held for instances only, and `Foo.print()` answered a Python binding
failure — `Object.print() missing 1 required positional argument: 'self'`.
"""

from __future__ import annotations

from abc import ABCMeta
from builtins import print as builtins_print
from functools import partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass
    from poop.types.string import Str


class class_side:  # noqa: N801
    """Binds a metaclass method to the class, ahead of same-named instance ones.

    `Foo.print` would otherwise never reach the metaclass: looking an attribute
    up on a class searches the class's own MRO before the metaclass, so
    `Object.print` wins and answers an unbound function — the exact failure the
    class side exists to remove. A *data* descriptor is consulted first, which
    is why `__set__` is defined here rather than left out.

    Instances are unaffected: instance lookup never consults the metaclass, so
    `Foo().print()` still finds `Object.print`.
    """

    __slots__ = ("_fn", "_name")

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn
        # Filled by __set_name__, which Python calls for every descriptor in a
        # class body — the only place this decorator is ever used.
        self._name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, cls: type | None, metacls: type) -> Any:
        if cls is None:
            return self
        return partial(self._fn, cls)

    def __set__(self, cls: type, value: object) -> None:
        raise AttributeError(self._name)


class PoopMeta(ABCMeta):
    """Metaclass giving every POOP class the class-side protocol.

    Derives from `ABCMeta`, not `type`: `Boolean(Object, ABC)` otherwise fails
    with "metaclass conflict: the metaclass of a derived class must be a
    (non-strict) subclass of the metaclasses of all its bases". It propagates
    for free — `ClassTransformer` already routes every user class through
    `Object`, and a metaclass is inherited.

    Every message here is a `class_side` descriptor, including the ones
    `Object` does not define today: a user class is free to declare its own
    `name` or `superclass` method, and the class side must still answer.
    """

    @class_side
    def name(cls) -> Str:
        from poop.types.string import Str

        return Str(cls.__name__)

    @class_side
    def superclass(cls) -> Any:
        from poop.types.none import none

        # Smalltalk answers nil for Object superclass, which is also how the
        # raw Python `object` at the root stays out of reach.
        bases = [base for base in cls.__bases__ if isinstance(base, PoopMeta)]
        if not bases:
            return none
        return bases[0]

    @class_side
    def has_attr(cls, name: Str) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(hasattr(cls, name._value))

    @class_side
    def print(
        cls,
        end: Str | NoneClass | None = None,
        flush: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        from poop.types._unwrap import _unwrap, _unwrap_bool
        from poop.types.none import none

        builtins_print(
            cls.__name__,
            end=_unwrap(end, "\n"),
            flush=_unwrap_bool(flush, False),
        )
        return none

    @class_side
    def does_not_understand(cls, name: str) -> Any:
        from poop.types._selectors import explain
        from poop.types.object import MessageNotUnderstood

        raise MessageNotUnderstood(explain(cls, name), name=name, obj=cls)

    if not TYPE_CHECKING:
        # Same reasoning as Object.__getattr__: a visible one answers Any for
        # every name and blinds `ty` to typos on every POOP class.
        def __getattr__(cls, name: str) -> Any:
            if name.startswith("__") and name.endswith("__"):
                raise AttributeError(name)
            return cls.does_not_understand(name)
