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

`__call__` covers the subclasses too. It used to read `cls.__dict__` and stop
there, which left the whole gap above open one level down — for the very
spelling this docstring calls a legal use of the name: `Stack([1, 2])` answered
a `Stack` holding one list, `N(4.9)` an `int` holding 4.9, and six of the
thirteen refused in Python's words. `_AliasMeta` now converts and rebuilds the
answer as the subclass. What the `__dict__` read was protecting is kept
explicitly: a subclass that declares its own `__init__` is built by it.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import copy
from itertools import takewhile
from typing import Any

from poop.types._cloak import cloak
from poop.types.meta import PoopMeta


def _payload_slots(cls: type) -> tuple[str, ...]:
    """Every slot a wrapper keeps its value in, down its whole MRO.

    `_value` for the scalars, `_items` for the sequences, `_data` for the
    mappings and sets, `_start`/`_stop`/`_step` for a `Range` — read off the
    declarations rather than tabulated here, so a new wrapper is covered by
    having `__slots__` at all, which every one of them must.
    """
    return tuple(
        slot for klass in cls.__mro__ for slot in getattr(klass, "__slots__", ())
    )


def _own_init(cls: type, alias: type) -> bool:
    """Whether a class between `cls` and `alias` declares its own `__init__`.

    Stops at the alias: everything from there down is the wrapper's own
    `__init__`, which is the "build from these elements" meaning this module
    exists to keep apart from converting.
    """
    above = takewhile(lambda klass: klass is not alias, cls.__mro__)
    return any("__init__" in klass.__dict__ for klass in above)


class _AliasMeta(PoopMeta):
    """Makes a class answer a call the way its converter does.

    Subclasses included. Reading `_converter` from `cls.__dict__` meant the
    whole "convert" / "build from these elements" gap this module closes was
    left open one level down — for the exact spelling the docstring above
    names as a legal use of a bare name (`class Stack(list)`). Every one of
    the thirteen constructors disagreed with itself there: `Stack([1, 2])`
    answered a `Stack` holding one list where `list([1, 2])` holds two
    elements, `N(4.9)` answered an `int` holding 4.9, and six refused
    outright, each naming a Python dunder, arity or slot.

    So the converter is looked up along the MRO, and the answer is rebuilt as
    `cls` — a subclass has the wrapper's slots, being a subclass. Two things
    keep their old meaning: a subclass declaring its own `__init__` is built
    by it (that is what the `__dict__` read was protecting), and a wrapper
    with no payload at all — `Boolean`, whose values are two singletons —
    cannot be rebuilt, so its converter's answer is passed through.
    """

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if "_converter" in cls.__dict__:
            return cls.__dict__["_converter"](*args, **kwargs)
        alias = _alias_in(cls)
        if _own_init(cls, alias):
            return super().__call__(*args, **kwargs)
        converted = alias.__dict__["_converter"](*args, **kwargs)
        slots = _payload_slots(alias.__dict__["_wrapped"])
        if not slots:
            return converted
        # `object.__new__`, not `cls.__new__`: the payload is about to be
        # written slot by slot, so the wrapper's own `__init__` must not run
        # over it — and no wrapper defines `__new__`.
        made = object.__new__(cls)
        for slot in slots:
            # Copied, not shared: a converter is free to answer a value it
            # was handed (`frozenset(fs)` answers `fs`), and two objects
            # sharing one list would be one object wearing two classes.
            setattr(made, slot, copy(getattr(converted, slot)))
        return made


def _alias_in(cls: type) -> Any:
    """The alias `cls` descends from.

    Always one: `_AliasMeta` is the metaclass of the aliases and of nothing
    else, so anything it is asked about is an alias or below one.
    """
    return next(klass for klass in cls.__mro__ if "_converter" in klass.__dict__)


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
