"""What a bare builtin *name* answers to, as opposed to a builtin call.

Every converter transformer has two rewrites: `visit_Call` sends `list(x)` to
the converter, and `visit_Name` sends a bare `list` to the wrapper class. The
two do different things — `_arity.py`'s docstring is entirely about that gap
("one name meant 'convert' at one arity and 'build from these elements' at
another, and only the first matches Python") — and it closed the gap for the
direct call only. Bind the name first and the call goes to the class:

    x = int
    x(4.9)          # an `int` holding 4.9, which then answers
                    # `float does not understand #+ with an int`
    x = list
    x([1, 2])       # [[1, 2]]
    x = tuple
    x([1, 2])       # ([1, 2],)

The first two rows are silent: nothing raises, and the program carries on with
a value whose class and contents disagree. A constructor is an object in POOP,
so this is not an exotic spelling — `[list, set].at(0)([1, 2])` and
`lambda c: c([1, 2])` are the same bug, and passing a converter as a block is
ordinary in a language whose iteration is `map`/`filter`.

The class cannot simply *be* the converter: `poop/types/` builds its values by
calling these classes directly (`Str(self._value.upper())`, `List(*elements)`),
and that is the "build from these elements" meaning. So the bare name binds an
**alias** instead — a subclass of the wrapper whose metaclass answers a call
with the converter, and which is still a class, because that is what the bare
name is otherwise used for:

    (5).is_instance(int)        # a type argument
    class Stack(list): ...      # a base
    int.name()                  # a class-side receiver

Only `__call__` is intercepted. The obvious companion — an `__instancecheck__`
delegating to the wrapped class, as `PoopExcMeta` does for the mirrors — does
not work here and is worth recording: the alias *is* a subclass of the wrapper,
so `ABCMeta.__subclasscheck__` walks `List.__subclasses__()`, reaches the alias,
and asks it the same question, which delegates back. It recurses until the stack
gives out. The type-argument case is answered one level up instead, by
`unalias` below, which the two `is_instance`/`is_subclass` pairs call.

`__call__` reads `cls.__dict__` rather than inheriting, for the reason
`PoopExcMeta.__instancecheck__` gives: a subclass must behave normally, or
`class Stack(list)` would answer a `List` from `Stack()`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from poop.types._cloak import cloak
from poop.types.meta import PoopMeta


class _AliasMeta(PoopMeta):
    """Makes a class answer a call the way its converter does."""

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        converter = cls.__dict__.get("_converter")
        if converter is None:
            return super().__call__(*args, **kwargs)
        return converter(*args, **kwargs)


def unalias(type_: Any) -> Any:
    """The wrapper behind a bare builtin name, for a type-*argument* position.

    `(5).is_instance(int)` hands over whatever `int` resolves to, which is now
    the alias — and an `Int` is not an instance of it, the alias being the
    subclass. Reading `_wrapped` restores the question the program asked.

    `__dict__`, not `getattr`: `_wrapped` is inherited by anything descending
    from the alias, so `class Stack(list)` would answer `List` here and
    `x.is_instance(Stack)` would be true of every list.
    """
    return getattr(type_, "__dict__", {}).get("_wrapped", type_)


def builtin_alias(wrapped: type, converter: Callable[..., Any], name: str) -> type:
    """The object a bare `<name>` binds to: `wrapped` that calls `converter`.

    A subclass rather than a wholly separate class, so a program subclassing
    the builtin (`class Stack(list)`) still descends from the real wrapper and
    inherits its messages. `_converter` is a `staticmethod` because it is a
    plain function living in a class body, which would otherwise bind `cls` as
    its first argument.
    """
    alias = _AliasMeta(
        name,
        (wrapped,),
        {
            "_converter": staticmethod(converter),
            "_wrapped": wrapped,
            "__slots__": (),
        },
    )
    # The same cloak the wrapper carries: `int.name()` and `repr(int)` must not
    # start answering something else because the name now resolves here.
    cloak(alias, name)
    return alias
