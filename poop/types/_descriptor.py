"""A message as a descriptor: a method read off an object answers a block.

`Object.__getattribute__` used to do this — one Python frame on *every*
attribute read in the language, including the library's own `self._value`,
to wrap the few reads that were a public bound method. Measured on 3.15, the
frame doubled the cost of a slot read (401 ns against 192) and was a third of
a message send. The hook is gone; each public method is a `message` instead,
a non-data descriptor installed where the class is built (`PoopMeta.__new__`,
and `_Mixin.__init_subclass__` for the shared mixins, which are not `PoopMeta`
classes). A `_`-name or a dunder is never a message and now resolves at C
speed; a public read binds through the original entry and wraps the result
in a `_MethodBlock` exactly when the hook would have — when what came back is
a `MethodType`, so a `staticmethod`, a `property` and a plain value stay
native, as before.

Non-data on purpose, like `Block.__get__`: consulted for a class attribute,
skipped for a name found in an instance's `__dict__`, so a block a user class
holds as state still reads back as itself.

`__func__` holds the innermost function, the convention `classmethod` and
`staticmethod` set, so `cloak._rename_own_functions` unwraps a `message` with
the `getattr(attr, "__func__", attr)` it already has. `_entry` holds what the
class body wrote — the function, or the `classmethod`/`staticmethod` around
it — and is what binding goes through.
"""

from types import FunctionType, MethodType
from typing import TYPE_CHECKING, Any, cast

from poop.types._late import late
from poop.types._selectors import is_message

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

# What a class body may write for a public method: the function, or the
# `classmethod`/`staticmethod` around one. All three bind through `__get__`.
type _Entry = FunctionType | classmethod[Any, Any, Any] | staticmethod[Any, Any]

# circular: block imports Object, which imports meta, which imports this.
# `block.py` installs `_MethodBlock` here the moment it exists; the getter is
# the fallback for a public method read before `block` has loaded.
_method_block: Callable[[], Callable[[MethodType], object]] = late(
    "poop.types.block", "_MethodBlock"
)
_METHOD_BLOCK: Callable[[MethodType], object] | None = None


def install_method_block(wrap: Callable[[MethodType], object]) -> None:
    """Called once by `poop/types/block.py`; see `_METHOD_BLOCK`."""
    global _METHOD_BLOCK  # noqa: PLW0603 — the one write, at import time
    _METHOD_BLOCK = wrap


class message:  # noqa: N801 — read as a word, like `class_side`
    """One public method of a POOP class, binding as the entry did."""

    __slots__ = ("__func__", "_entry")

    def __init__(self, entry: _Entry) -> None:
        self._entry = entry
        self.__func__ = getattr(entry, "__func__", entry)

    def __get__(self, instance: object, owner: type | None = None) -> Any:  # noqa: ANN401 — a bound method of any shape
        bound = self._entry.__get__(instance, owner)
        if instance is not None and type(bound) is MethodType:
            wrap = _METHOD_BLOCK
            return (wrap if wrap is not None else _method_block())(bound)
        return bound


def _is_plain_function_entry(entry: object) -> bool:
    return type(getattr(entry, "__func__", entry)) is FunctionType


def messages_in(namespace: Mapping[str, object]) -> dict[str, message]:
    """The entries of a class body that become `message`s, wrapped.

    A public name (`is_message`) whose entry is a function, or a
    `classmethod`/`staticmethod` around one. A `property`, a `class_side`, a
    `Block` installed by `set_attr` and a plain value are left as they are.
    """
    return {
        name: message(cast("_Entry", entry))
        for name, entry in namespace.items()
        if is_message(name)
        and not isinstance(entry, message)
        and _is_plain_function_entry(entry)
    }


def instance_only(entry: object) -> bool:
    """Whether a class-dict entry is a plain method — one only an instance answers.

    `PoopMeta.__getattribute__` refuses such a method read off the class; a
    `classmethod`, `staticmethod`, `property` or `class_side` keeps answering
    class-side. A `message` is asked about what it wraps.
    """
    if isinstance(entry, message):
        entry = entry._entry
    return type(entry) is FunctionType
