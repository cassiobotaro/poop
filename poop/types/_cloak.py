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
"""

from __future__ import annotations


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
