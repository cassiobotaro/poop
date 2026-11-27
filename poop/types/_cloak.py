"""The one place a wrapper's Python identity is rewritten.

Every wrapper answers to the name of the builtin it replaces: `Int` reads back
as `int`, `Block` as `function`, `ListIterator` as `list_iterator`. The cloak
covers `__qualname__` as well as `__name__` and `__module__`, because CPython
prefers it in several of its own messages, and Python 3.14's unhashable-key
error puts both spellings in one sentence:

    {[1]: 2}  ->  cannot use 'list' as a dict key (unhashable type: 'list')

Setting the three together makes a mismatch there unrepresentable rather than
merely tested: there is no way to patch one and forget the others.

Three, though, is still only the class's own identity. CPython composes a
*call-signature* error from the **function's** `__qualname__`, frozen when the
class body runs and not touched by renaming the class — so `cloak` renames the
functions a class owns too, and a wrong-arity message answers in the names a
program writes:

    "abc".upper(1)   ->  TypeError: str.upper() takes 1 positional argument ...
    [1].append()     ->  TypeError: list.append() missing 1 required ...

Left alone, those would read `Str.upper()` and `List.append()`, and a mixin's
method `_IterableMixin.map()` — exactly what `_reject_private` refuses to hand
out ("POOP objects do not expose their internals"). `cloak_callable` does the
same for a bare function: the `_poop_*` rewriter helpers, whose spelling is one
`no_poop_prefix` *reserves*, so the interpreter would otherwise name something
it then refuses.
"""

from types import FunctionType
from typing import Protocol


class Renamable(Protocol):
    """What `cloak_callable` writes: the three names a function carries.

    A plain function has all three and they are writable; a `Callable` says
    nothing about them. The protocol states exactly the contract, so a
    descriptor holding its function under a precise `Callable`-shaped type
    can still hand it over.
    """

    __name__: str
    __qualname__: str
    __module__: str


def cloak_callable(fn: Renamable, name: str) -> None:
    """Hide a plain function's Python identity behind `name`.

    For the rewriter helpers bound into `DEFAULT_NAMESPACE` under a mangled
    `_poop_*` key, and for the class-side messages. The key stays mangled —
    only the spelling CPython reports changes, so `range(1, 2, 3, 4)` blames
    `range`, not `_poop_range`.
    """
    fn.__name__ = name
    fn.__qualname__ = name
    fn.__module__ = "builtins"


def _rename_own_functions(cls: type, name: str) -> None:
    """Point every function `cls` defines at the cloaked class name.

    Only `vars(cls)` — the functions this class owns. An inherited one belongs
    to the class that defined it and is renamed when *that* class is cloaked,
    so a shared mixin method is renamed once, at its own definition site,
    rather than once per subclass with the last writer winning.
    """
    for attr in vars(cls).values():
        # Unwrap the descriptor so `classmethod` / `staticmethod` are covered:
        # `Int.from_bytes` is a classmethod and reports its arity like any other.
        fn = getattr(attr, "__func__", attr)
        if isinstance(fn, FunctionType):
            fn.__qualname__ = f"{name}.{fn.__name__}"


def cloak(cls: type, name: str) -> None:
    """Hide `cls`'s Python identity behind the name it answers to.

    `name` is the builtin's spelling. `Try` and `With` pass their own: both
    are legitimate user-facing names, and only their module would leak.
    Applied by `Object.__init_subclass__` from the `name=` class keyword;
    called directly only for the classes built by hand.
    """
    cls.__module__ = "builtins"
    cls.__name__ = name
    # The half CPython reaches for when it composes a message about a type it
    # was handed. Left alone it answers the internal spelling.
    cls.__qualname__ = name
    _rename_own_functions(cls, name)
