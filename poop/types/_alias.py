"""What a bare builtin *name* answers to, as opposed to a builtin call.

Every converter transformer has two rewrites: `visit_Call` sends `list(x)` to
the converter, and `visit_Name` sends a bare `list` to a class. The converter
and the wrapper class do different things — `_arity.py`'s docstring is
entirely about that gap ("one name meant 'convert' at one arity and 'build
from these elements' at another, and only the first matches Python") — and
`_arity.py` keeps them apart for the direct call. Bind the name first and the
call goes to the class, so that class has to convert as well:

    x = int
    x(4.9)          # 4, where the wrapper would hold 4.9
    x = list
    x([1, 2])       # [1, 2], where the wrapper would answer [[1, 2]]
    x = tuple
    x([1, 2])       # (1, 2), where the wrapper would answer ([1, 2],)

The wrapper's answers would be silent in the first two rows: nothing raises,
and the program carries on with a value whose class and contents disagree. A
constructor is an object in POOP, so this is not an exotic spelling —
`[list, set].at(0)([1, 2])` and `lambda c: c([1, 2])` are the same call, and
passing a converter as a block is ordinary in a language whose iteration is
`map`/`filter`.

The class cannot simply *be* the converter: `poop/types/` builds its values by
calling these classes directly (`Str(self._value.upper())`, `List(*elements)`),
and that is the "build from these elements" meaning. So the bare name binds an
**alias** instead — a subclass of the wrapper whose metaclass answers a call
with the converter, and which is still a class, because that is what the bare
name is otherwise used for:

    (5).is_instance(int)        # a type argument
    class Stack(list): ...      # a base
    int.name()                  # a class-side receiver

Only `__call__` is intercepted, not `__instancecheck__` as `PoopExcMeta` does
for the mirrors (`doc/adr/0051-a-bare-builtin-name-is-the-converter-alias.md`).
The type-argument case is answered one level up instead, by `unalias` below,
which the two `is_instance`/`is_subclass` pairs call.

`__call__` covers the subclasses too, for the very spelling this docstring
calls a legal use of the name: `Stack([1, 2])` answers a `Stack` holding two
elements and `N(4.9)` an `N` holding 4. `_AliasMeta` converts and rebuilds the
answer as the subclass, except that a subclass which declares its own
`__init__` is built by it.
"""

from copy import copy
from itertools import takewhile
from typing import TYPE_CHECKING, overload

from poop.types import mirrors
from poop.types._cloak import cloak
from poop.types.meta import PoopMeta

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


def _payload_slots(cls: type) -> tuple[str, ...]:
    """Every slot a wrapper keeps its value in, down its whole MRO.

    `_value` for the scalars, `_items` for the sequences, `_data` for the
    mappings and sets, `_start`/`_stop`/`_step` for a `Range` — read off the
    declarations rather than tabulated here, so a new wrapper is covered by
    having `__slots__` at all, which every one of them must.
    """
    return tuple(*getattr(klass, "__slots__", ()) for klass in cls.__mro__)


def _own_init(cls: type, alias: type) -> bool:
    """Whether a class between `cls` and `alias` declares its own `__init__`.

    Stops at the alias: everything from there down is the wrapper's own
    `__init__`, which is the "build from these elements" meaning this module
    exists to keep apart from converting.
    """
    above = takewhile(lambda klass: klass is not alias, cls.__mro__)
    return any("__init__" in klass.__dict__ for klass in above)


def _fill(made: object, converted: object, slots: tuple[str, ...]) -> None:
    """Write `converted`'s payload into `made`, slot by slot.

    Copied, not shared: a converter is free to answer a value it was handed
    (`frozenset(fs)` answers `fs`), and two objects sharing one list would be
    one object wearing two classes.
    """
    for slot in slots:
        setattr(made, slot, copy(getattr(converted, slot)))


def _endow(
    made: object,
    cls: type,
    alias: type,
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> None:
    """Give `made` a payload before its own `__init__` runs.

    The `__new__` step Python has and POOP does not. CPython builds the value
    in `__new__`, from the *constructor's* arguments, before `__init__` is
    reached, and the two families differ there: `int.__new__` consumes the
    arguments, so `class N(int)` whose `__init__` ignores them still answers
    `4` for `N(4.9)`; `list.__new__` ignores them and hands `__init__` an
    empty list, so `class Pair(list)` with a signature of its own is an
    ordinary empty list carrying whatever state it set. Writing the payload in
    `__init__` alone would leave a subclass that never passes it up with no
    payload at all, and its first message would answer `#_value` — the
    internal slot name.

    One positional argument and no keywords is the shape every converter
    takes, so it converts. Otherwise the arguments are the subclass's own and
    the wrapper's empty value stands in — and when there is none to stand in
    (an `int` has no empty), the object cannot be built at all, which is what
    CPython answers there too.
    """
    # Read off the alias like `_converter` and `_empty` beside it, rather
    # than handed in: three facts about one alias, found one way.
    slots = alias.__dict__["_slots"]
    if len(args) == 1 and not kwargs:
        _fill(made, alias.__dict__["_converter"](*args), slots)
        return
    empty = alias.__dict__["_empty"]
    if empty is None:
        raise mirrors.TypeError(
            f"this {cls.__name__} was built without its value — "
            "a class built on a builtin must pass one up from its constructor"
        )
    _fill(made, empty, slots)


class _AliasMeta(PoopMeta):
    """Makes a class answer a call the way its converter does.

    Subclasses included. The converter is looked up along the MRO, not read
    from `cls.__dict__`, which would leave the "convert" / "build from these
    elements" gap this module closes open one level down — for the exact
    spelling the docstring above names as a legal use of a bare name (`class
    Stack(list)`), where `Stack([1, 2])` would answer a `Stack` holding one
    list while `list([1, 2])` holds two elements.

    The answer is rebuilt as `cls` — a subclass has the wrapper's slots, being
    a subclass. Two exceptions: a subclass declaring its own `__init__` is
    built by it, and a wrapper with no payload at all — `Boolean`, whose
    values are two singletons — cannot be rebuilt, so its converter's answer
    is passed through.
    """

    # A type variable rather than `Self`, which ty refuses in a metaclass.
    def __new__[M: _AliasMeta](  # noqa: PYI019
        mcls: type[M],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        /,
        **kwargs: object,
    ) -> M:
        """Build the class, refusing a base that has no value to give.

        `bool` is the one wrapper whose values are singletons with no payload,
        and CPython refuses it as a base outright (`type 'bool' is not an
        acceptable base type`). Defining the class and failing at the first
        instance would answer a dozen dunders in one sentence, from a program
        that spelled none. Refusing where CPython refuses says the same thing in
        POOP's words, and at the line that made the decision.
        """
        for base in bases:
            wrapped = base.__dict__.get("_wrapped")
            if wrapped is not None and not _payload_slots(wrapped):
                raise mirrors.TypeError(
                    f"{base.__name__} cannot be subclassed — "
                    "its values are the whole class"
                )
        return super().__new__(mcls, name, bases, namespace, **kwargs)

    def __call__(cls, *args: object, **kwargs: object) -> object:
        # Every class `_AliasMeta` is asked about descends from an alias — it
        # is the metaclass of the aliases and of nothing else — so the first
        # one up the MRO is there to be found, and is `cls` itself when the
        # bare name was called.
        alias = next(_aliases_in(cls))
        converter = alias.__dict__["_converter"]
        if alias is cls:
            return converter(*args, **kwargs)
        if _own_init(cls, alias):
            # The `__new__` step Python has and POOP does not — `_endow` says
            # why, and why one positional argument converts while any other
            # shape is the subclass's own signature for `__init__` to read.
            #
            # Every wrapper reachable here has a payload: the one that does
            # not, `Boolean`, cannot be subclassed at all — `__new__` above
            # refuses it where CPython refuses it.
            made = object.__new__(cls)
            _endow(made, cls, alias, args, kwargs)
            made.__init__(*args, **kwargs)
            return made
        converted = converter(*args, **kwargs)
        # `object.__new__`, not `cls.__new__`: the payload is about to be
        # written slot by slot, so the wrapper's own `__init__` must not run
        # over it — and no wrapper defines `__new__`.
        made = object.__new__(cls)
        _fill(made, converted, alias.__dict__["_slots"])
        return made


def _aliases_in(cls: type) -> Iterator[type]:
    """The aliases on `cls`'s MRO, nearest first — at most one, in practice.

    `_AliasMeta.__call__` takes the first and is always handed one;
    `wrapped_instance` below asks about the plain wrappers too, which have
    none, and so reads with a default.
    """
    return (klass for klass in cls.__mro__ if "_converter" in klass.__dict__)


def wrapped_instance[T](cls: type[T], *args: object) -> T:
    """An instance of `cls`, built by the wrapper's constructor.

    For POOP's own class-side constructors — `bytes.fromhex`, `int.from_bytes`,
    `float.fromhex` — which hold a finished *Python* value and need it wrapped.
    Not `cls(...)`: `cls` is whatever the program named, and under a bare
    builtin name it is the alias, whose call is the converter, and a converter
    takes what a program writes rather than a raw value. `cls(...)` would
    break `bytes.fromhex("6162")`, the only spelling a reader would use, while
    `b"".fromhex("6162")` sent to an instance works.

    Three receivers, three answers. The alias answers the wrapper's own
    instance; a plain wrapper builds itself; a program's subclass is built
    from the wrapper's constructor so `class B(bytes)` still answers a `B`.
    """
    wrapper = unalias(cls)
    if wrapper is not cls:
        return wrapper(*args)
    alias = next(_aliases_in(cls), None)
    if alias is None:
        return cls(*args)
    made = object.__new__(cls)
    alias.__dict__["_wrapped"].__init__(made, *args)
    return made


@overload
def unalias(type_: type) -> type: ...
@overload
def unalias(type_: object) -> object: ...
def unalias(type_: object) -> object:
    """The wrapper behind a bare builtin name, for a type-*argument* position.

    `(5).is_instance(int)` hands over whatever `int` resolves to, which is
    the alias — and an `Int` is not an instance of it, the alias being the
    subclass. Reading `_wrapped` restores the question the program asked.

    `__dict__`, not `getattr`: `_wrapped` is inherited by anything descending
    from the alias, so `class Stack(list)` would answer `List` here and
    `x.is_instance(Stack)` would be true of every list.
    """
    return getattr(type_, "__dict__", {}).get("_wrapped", type_)


def builtin_alias(wrapped: type, converter: Callable[..., object], name: str) -> type:
    """The object a bare `<name>` binds to: `wrapped` that calls `converter`.

    A subclass rather than a wholly separate class, so a program subclassing
    the builtin (`class Stack(list)`) still descends from the real wrapper and
    inherits its messages. `_converter` is a `staticmethod` because it is a
    plain function living in a class body, which would otherwise bind `cls` as
    its first argument.
    """

    # Fixed when the alias is built, so read off the wrapper's MRO once.
    slots = _payload_slots(wrapped)

    def __init__(self: object, *args: object, **kwargs: object) -> None:  # noqa: N807 — installed as the alias's
        """`super().__init__(...)` from a subclass — and it converts.

        The convert/build gap at the constructor. `no_dunder_attribute`
        carves out exactly one dunder call, `__init__`, *for* this spelling, so
        it is the constructor a program is invited to write — and the
        wrapper's variadic `__init__` means "build from these elements":
        reaching it, `class S(list)` calling `super().__init__(xs)` would
        answer a list holding one list, and only `super().__init__(*xs)` would
        work, with nothing to say so.

        The alias sits between the subclass and the wrapper in the MRO
        (`S.__mro__` is `(S, <alias>, List, …)`), which is exactly where
        `super()` looks, so this intercepts that call and nothing else.
        """
        _fill(self, converter(*args, **kwargs), slots)

    try:
        # The wrapper's empty value, when it has one: `list()`, `dict()`,
        # `set()`, `tuple()` — the families whose `__new__` hands `__init__`
        # something to fill. An `int` has no empty, and CPython says so too.
        empty: object = wrapped()
    except TypeError:
        empty = None

    alias = _AliasMeta(
        name,
        (wrapped,),
        {
            "_converter": staticmethod(converter),
            "_wrapped": wrapped,
            "_slots": slots,
            "_empty": empty,
            "__init__": __init__,
            "__slots__": (),
        },
    )
    # The same cloak the wrapper carries: `int.name()` and `repr(int)` must not
    # start answering something else because the name now resolves here.
    cloak(alias, name)
    return alias
