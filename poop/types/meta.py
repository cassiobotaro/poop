"""The class side of POOP — classes are objects and answer messages.

Smalltalk's "everything is an object" includes classes: `Foo name`, `Foo
superclass` are ordinary messages to an ordinary object. Without this, POOP's
thesis held for instances only, and `Foo.print()` answered a Python binding
failure — `Object.print() missing 1 required positional argument: 'self'`.
"""

from __future__ import annotations

import builtins
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
        # Imported here, not at module scope: `exceptions` builds its classes
        # through `PoopMeta`, so the dependency only runs one way at import.
        from poop.types.exceptions import MIRRORS

        raise MIRRORS["AttributeError"](self._name)


def _reject_dunder(name: str) -> None:
    """The class-side half of `no_dunder_attribute`, mirroring `Object`'s.

    Both read the same `dunder_message`, so the ban says one thing whether the
    receiver is an instance or a class.
    """
    from poop.types.exceptions import MIRRORS
    from poop.validators.no_dunder_attribute import dunder_message

    message = dunder_message(name)
    if message is not None:
        raise MIRRORS["AttributeError"](message.lstrip("."))


def _reject_private(name: str) -> None:
    """The class-side half of `Object._reject_private` — refuse `_`-privates.

    A class is an object too, so `Foo.get_attr("_data")` must be refused for the
    same reason the instance side refuses it: it reaches internals the mangling
    scheme exists to hide.
    """
    from poop.types.exceptions import MIRRORS

    is_dunder = name.startswith("__") and name.endswith("__")
    if name.startswith("_") and not is_dunder:
        raise MIRRORS["AttributeError"](
            f"{name} is private — POOP objects do not expose their internals"
        )


def _checked_name(name: Str) -> str:
    """The raw name behind `name`, both class-side bans applied.

    The class-side twin of `Object._checked_name`, down to `_attr_name`
    keeping a non-`Str` name from leaking `#_value`: `Foo.get_attr([1])` used
    to answer `list does not understand #_value` exactly as the instance side
    did.
    """
    from poop.types._unwrap import _attr_name

    raw = _attr_name(name)
    _reject_dunder(raw)
    _reject_private(raw)
    return raw


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

        return to_boolean(hasattr(cls, _checked_name(name)))

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

        # Mirror `Object.dir`: hide every `_`-prefixed name so the class side
        # never leaks dunders or the mangled `_poop_*` internals.
        return List(
            *(Str(name) for name in builtins_dir(cls) if not name.startswith("_"))
        )

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

    # The rest of `Object`'s protocol, each the substitute for a construct
    # banned on a class too: `Foo is Bar` (no_is), `isinstance(Foo, T)`
    # (no_isinstance), `getattr`/`setattr`/`delattr` (no_getattr/…),
    # `assert Foo` (no_assert). Without them the ban named a substitute that
    # did not exist on the receiver — item 14's original contradiction, which
    # its first pass measured short by nine.

    @class_side
    def is_identical(cls, other: Any) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(cls is other)

    @class_side
    def not_identical(cls, other: Any) -> Boolean:
        from poop.types.boolean import false, true

        return false if cls is other else true

    @class_side
    def is_instance(cls, type_: type) -> Boolean:
        from poop.types.boolean import to_boolean

        # A class is an instance of its metaclass, not of its own bases, so
        # `Foo.is_instance(Object)` is `false` — `Foo.is_subclass(Object)` is
        # the "descends from" question.
        return to_boolean(isinstance(cls, type_))

    @class_side
    def if_none(cls, block: Callable[[], Any]) -> Any:
        # A class is never none, so this answers the class unchanged.
        return cls

    @class_side
    def if_not_none(cls, block: Callable[[Any], Any]) -> Any:
        return block(cls)

    @class_side
    def assert_(cls, message: Str | NoneClass | None = None) -> Any:
        # A class is always truthy, so the assertion always holds and answers
        # the class; the failing branch `Object.assert_` has is unreachable.
        return cls

    @class_side
    def get_attr(cls, name: Str, *default: Any) -> Any:
        from poop.types.block import _as_block

        # Same wrap as the instance side: a class-side method answered a raw
        # Python function, which understands no message.
        return _as_block(builtins.getattr(cls, _checked_name(name), *default))

    @class_side
    def set_attr(cls, name: Str, value: Any) -> NoneClass:
        from poop.types.none import none

        builtins.setattr(cls, _checked_name(name), value)
        return none

    @class_side
    def del_attr(cls, name: Str) -> NoneClass:
        from poop.types.none import none

        builtins.delattr(cls, _checked_name(name))
        return none

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
            # Native on purpose, like `Object.__getattr__`: Python's own
            # attribute probe, answered before `exceptions` has finished
            # building the table a mirror would come from.
            if name.startswith("__") and name.endswith("__"):
                raise AttributeError(name)
            return cls.does_not_understand(name)
