"""The one place a wrapper's Python identity is rewritten.

Every wrapper answers to the name of the builtin it replaces: `Int` reads back
as `int`, `Block` as `function`, `ListIterator` as `list_iterator`. That cloak
was three separate assignments repeated down the tail of every module, and it
covered `__name__` and `__module__` but not `__qualname__` — which CPython
prefers in several of its own messages. Python 3.14's unhashable-key error put
both spellings in one sentence:

    {[1]: 2}  ->  cannot use 'List' as a dict key (unhashable type: 'list')

Setting the three together makes that unrepresentable rather than merely
tested: there is no way to patch one and forget the others.

Three, though, was still only the class's own identity. CPython composes a
*call-signature* error from the **function's** `__qualname__`, frozen when the
class body ran and never touched by the cloak — so every wrong-arity message in
the language answered in POOP's internal vocabulary, names user code cannot
even write:

    "abc".upper(1)   ->  TypeError: Str.upper() takes 1 positional argument ...
    [1].append()     ->  TypeError: List.append() missing 1 required ...
    [1, 2].map()     ->  TypeError: _IterableMixin.map() missing 1 required ...

The last is the sharpest: `_IterableMixin` is exactly what `_reject_private`
refuses to hand out ("POOP objects do not expose their internals"). `cloak` now
renames the functions a class owns, and `cloak_callable` does the same for a
bare function — the `_poop_*` rewriter helpers, whose leaked spelling is one
`no_poop_prefix` *reserves*, so the interpreter was naming something it would
then refuse.
"""

from __future__ import annotations

from types import FunctionType


def cloak_callable(fn: FunctionType, name: str) -> None:
    """Hide a plain function's Python identity behind `name`.

    For the rewriter helpers bound into `DEFAULT_NAMESPACE` under a mangled
    `_poop_*` key. The key stays mangled — only the spelling CPython reports
    changes, so `range(1, 2, 3, 4)` blames `range`, not `_poop_range`.

    `FunctionType`, not a `Callable` protocol: only a real function carries the
    writable `__name__` / `__qualname__` this sets, and it is what the caller
    has already narrowed to.
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


def cloak(cls: type, name: str | None = None) -> None:
    """Hide `cls`'s Python identity behind the name it answers to.

    `name` is the builtin's spelling; omitting it keeps the class's own name
    and only drops the module path, which is what `Try` and `With` need — both
    are legitimate user-facing names, and only `poop.types.try_` leaked.
    """
    cls.__module__ = "builtins"
    if name is not None:
        cls.__name__ = name
        # The half CPython reaches for when it composes a message about a
        # type it was handed. Left alone it answers the internal spelling.
        cls.__qualname__ = name
        _rename_own_functions(cls, name)
