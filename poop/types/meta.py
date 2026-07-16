"""The class side of POOP — classes are objects and answer messages.

Smalltalk's "everything is an object" includes classes: `Foo name`, `Foo
superclass` are ordinary messages to an ordinary object. Without this, POOP's
thesis held for instances only, and `Foo.print()` answered a Python binding
failure — `Object.print() missing 1 required positional argument: 'self'`.
"""

from __future__ import annotations

from abc import ABCMeta
from builtins import (
    dir as builtins_dir,
)
from builtins import (
    format as builtins_format,
)
from builtins import (
    hash as builtins_hash,
)
from builtins import (
    id as builtins_id,
)
from builtins import (
    print as builtins_print,
)
from functools import partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
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


def _refuse(cls: type, name: str) -> None:
    """Refuse an instance-only message, naming the class-side one instead.

    Not routed through `does_not_understand`: its difflib hint would answer
    `#class_` with "did you mean #class_name?", which is refused here too —
    sending the reader from one refusal to another.
    """
    from poop.types.object import MessageNotUnderstood

    raise MessageNotUnderstood(
        f"{cls.__name__} does not understand #{name} — "
        f"#{name} asks an instance about its class; a class answers #name",
        name=name,
        obj=cls,
    )


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

    # `Object`'s protocol, answered class-side. Each needs its own descriptor:
    # a metaclass cannot inherit these into class-side lookup, which is the
    # whole reason `class_side` exists. Without them the bans contradict
    # themselves — `hash(Foo)` answers "use obj.hash() instead" while
    # `Foo.hash()` answered a binding error.

    @class_side
    def hash(cls) -> Int:
        from poop.types.int import Int

        return Int(builtins_hash(cls))

    @class_side
    def id(cls) -> Int:
        from poop.types.int import Int

        return Int(builtins_id(cls))

    @class_side
    def is_none(cls) -> Boolean:
        from poop.types.boolean import false

        return false

    @class_side
    def not_none(cls) -> Boolean:
        from poop.types.boolean import true

        return true

    @class_side
    def not_(cls) -> Boolean:
        from poop.types.boolean import false

        # A class is always truthy, so this is constant — but it has to exist:
        # `not x` is banned and `x.not_()` is the substitute.
        return false

    @class_side
    def callable(cls) -> Boolean:
        from poop.types.boolean import true

        # Always true: calling a class is how you build an instance.
        return true

    @class_side
    def repr(cls) -> Str:
        from poop.types.string import Str

        # The class's name, matching `print` and Smalltalk's `Foo printString`.
        # `builtins.repr(cls)` would answer `<class 'builtins.Foo'>`, putting
        # Python's vocabulary inside a POOP message's answer.
        return Str(cls.__name__)

    @class_side
    def ascii(cls) -> Str:
        from poop.types.string import Str

        # Same text as `repr`, with any non-ASCII escaped — a class name is an
        # identifier, and Python 3 lets those hold non-ASCII.
        escaped = cls.__name__.encode("ascii", "backslashreplace")
        return Str(escaped.decode("ascii"))

    @class_side
    def dir(cls) -> List:
        from poop.types.list import List
        from poop.types.string import Str

        return List(*(Str(name) for name in builtins_dir(cls)))

    @class_side
    def format(cls, spec: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap
        from poop.types.string import Str

        return Str(builtins_format(cls.__name__, _unwrap(spec, "")))

    @class_side
    def class_(cls) -> Any:
        # Smalltalk answers the metaclass here — `Foo class` is `Foo class`.
        # POOP has none to answer with: `PoopMeta` is not itself a POOP class
        # (`type(PoopMeta)` is `type`), so handing it back would leak exactly
        # the raw class object the class side exists to remove. Refusing and
        # naming `name` teaches; answering `Foo` would quietly make
        # `class_name` mean one thing on an instance and another on a class.
        _refuse(cls, "class_")

    @class_side
    def class_name(cls) -> Any:
        _refuse(cls, "class_name")

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
