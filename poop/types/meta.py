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
    print as builtins_print,
)
from functools import partial, wraps
from types import FunctionType
from typing import TYPE_CHECKING, Any, Never

from poop.types._cloak import cloak_callable

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

    `refuses` marks the descriptors that answer nothing but a refusal, so
    `__dir__` below can leave them out. A flag rather than a list of names in
    this module, for the reason `_EXEMPT` in `test_mirrored_raises.py` gives:
    a list has to be kept in step by hand, and a new refusal added without
    touching it would be advertised as a message.
    """

    __slots__ = ("_fn", "_name", "refuses")

    def __init__(self, fn: FunctionType, *, refuses: bool = False) -> None:
        self._fn = fn
        self.refuses = refuses
        # Filled by __set_name__, which Python calls for every descriptor in a
        # class body — the only place this decorator is ever used.
        self._name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name
        # The one moment the function knows the message it answers. `cloak`
        # renames the functions in `vars(cls)` and unwraps `classmethod` /
        # `staticmethod` through `__func__`, but a `class_side` descriptor
        # keeps its function in `_fn` and `PoopMeta` is never cloaked at all —
        # so the class side, a documented user-facing surface, still composed
        # its wrong-arity errors from POOP's internal vocabulary:
        # `PoopMeta.name() takes 1 positional argument but 2 were given`, a
        # name a program cannot write and cannot reach. Answering `Foo.print()`
        # instead is not available here: one function is shared by every class,
        # and `__qualname__` is fixed when the class body runs.
        cloak_callable(self._fn, name)

    def __get__(self, cls: type | None, metacls: type) -> Any:
        if cls is None:
            return self
        return partial(self._fn, cls)

    def __set__(self, cls: type, value: object) -> None:
        # Imported here, not at module scope: `exceptions` builds its classes
        # through `PoopMeta`, so the dependency only runs one way at import.
        from poop.types.exceptions import MIRRORS

        # A sentence, not the bare name: `AttributeError: name` read as if the
        # *word* `name` were the problem, and both spellings of the mistake —
        # `Foo.name = 5` and the sanctioned `Foo.set_attr("name", 5)` — landed
        # on it. `_reject_private`, ten lines down, is the model.
        raise MIRRORS["AttributeError"](
            f"#{self._name} is answered by every class — it cannot be rebound"
        )


def class_side_refusal(fn: FunctionType) -> class_side:
    """A class-side descriptor that only ever refuses.

    The decorator form of `class_side(fn, refuses=True)` — `@class_side(...)`
    cannot spell it, since the decorator *is* the descriptor's constructor.
    Reads as its own word at the call site, which is the point: the reader of
    `@class_side_refusal` knows before the body what the method answers.
    """
    return class_side(fn, refuses=True)


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


def _reject_builtin(cls: type) -> None:
    """Refuse a write to a class POOP defines rather than the program.

    `__slots__` is what keeps state off the instance side, and every wrapper
    declares one — `Object.set_attr` even has a sentence for that refusal. The
    class side had no equivalent, and `class_()` hands the class out, so
    `"abc".class_().del_attr("upper")` removed `upper` from every string in
    the program and `(5).class_().set_attr("bit_length", block)` replaced a
    message on `int`. The only names that happened to be safe were the
    `class_side` descriptors, whose `__set__` refuses.

    `__module__` is the discriminator already in place: `cloak` puts every
    wrapper and every mirror in `builtins`, while a class a POOP program
    defines carries `__poop__` from `_ALLOWED_BUILTINS["__name__"]`. It cannot
    be forged either — `__module__` is a dunder, so `no_dunder_attribute`
    refuses the literal spelling and `_reject_dunder` the computed one.
    """
    from poop.types.exceptions import MIRRORS

    if cls.__module__ == "builtins":
        raise MIRRORS["AttributeError"](
            f"{cls.__name__} is a POOP builtin — its messages cannot be "
            "changed; only a class you defined can be"
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


def _instance_only(cls: type, name: str) -> bool:
    """Whether `name` resolves to a plain method — one only an instance answers.

    Read off the MRO's dicts rather than through `getattr`, which is what
    `__getattribute__` below has already intercepted. A `classmethod`,
    `staticmethod`, `property` or `class_side` descriptor is not a
    `FunctionType` here, so each keeps answering class-side as before.
    """
    for klass in type.__getattribute__(cls, "__mro__"):
        if name in vars(klass):
            return type(vars(klass)[name]) is FunctionType
    return False


def _reflected(cls: type, name: str) -> Any:
    """`name` on `cls`, past the instance-side refusal.

    `get_attr` / `has_attr` are the *reflective* substitutes `no_getattr`
    names, and asking a class for one of its methods by name is a different
    act from writing the message: the answer is the unbound function, which
    takes its receiver explicitly exactly as it does in Python. `getattr`
    itself now goes through `__getattribute__` and would be refused, so these
    two read past it. Raises `AttributeError` when there is nothing there, as
    `getattr` does, but never consults `__getattr__` — the callers decide what
    a missing name means.
    """
    return type.__getattribute__(cls, name)


def _refuse_instance_side(cls: type, name: str) -> None:
    """Refuse a method the *instance* answers, reached through the class.

    `class_side` exists to remove one failure — `INFECTIONS.md`: "the bans
    contradicted themselves: `hash(Foo)` answers 'use `obj.hash()` instead'
    while `Foo.hash()` answered a binding error, naming a substitute that did
    not exist on that receiver". It removed it for `Object`'s protocol; the
    wrapper's own messages were left, so `str.upper()` answered `str.upper()
    missing 1 required positional argument: 'self'` — naming `self`, a
    receiver POOP never spells, and "positional argument", which the wording
    sweep bans outright. 64 of the 90 names `str.dir()` listed answered that.

    The sentence is the shape `_refuse` and `_refuse_native` already use, so
    the whole family reads like `class_` instead of like a binding failure.
    """
    from poop.types.object import MessageNotUnderstood

    raise MessageNotUnderstood(
        f"{cls.__name__} does not understand #{name} — "
        f"#{name} asks an instance; send it to one",
        name=name,
        obj=cls,
    )


def _refuse_native(cls: type, name: str, instead: str) -> None:
    """Refuse a name POOP never meant to offer, naming the message that does.

    `type.mro` and `ABCMeta.register` arrive on every POOP class with the
    metaclass, carry no leading underscore, and answer raw Python — but they
    are not messages POOP designed, so `_refuse`'s wording ("asks an instance
    about its class") says nothing true about them.
    """
    from poop.types.object import MessageNotUnderstood

    raise MessageNotUnderstood(
        f"{cls.__name__} does not understand #{name} — "
        f"#{name} is Python's; a class answers #{instead}",
        name=name,
        obj=cls,
    )


# The protocol slots CPython reads directly, with the native each one must
# answer and the POOP type a program can actually build. A POOP method can
# only return a POOP value, so every one of these was unsatisfiable from
# inside the language: `def __str__(self): return "P!"` answered `TypeError:
# __str__ returned non-string (type str)` — a sentence that names `str` as the
# thing that is not a `str`, because `_cloak` renamed the wrapper to the
# builtin it stands for. `__bool__` was worse (`should return bool, returned
# bool`), and `__hash__` printed `__poop__.P`, the marker `_reject_builtin`
# uses to tell a user's class from a builtin.
_PROTOCOL_SLOTS: dict[str, tuple[type, str, str]] = {
    "__str__": (str, "str", "text"),
    "__repr__": (str, "str", "repr"),
    "__bool__": (bool, "bool", "truth"),
    "__hash__": (int, "int", "hash"),
    "__len__": (int, "int", "length"),
}


def _adapted(slot: str, method: Any) -> Any:
    """`method` with its POOP answer unwrapped for CPython's protocol.

    Wrapping happens where the class is built, so the wrappers in
    `poop/types/` — which are written in Python and already answer natives —
    pass through untouched: `to_python` is identity for a value that is
    already one.
    """
    native, spelling, role = _PROTOCOL_SLOTS[slot]

    @wraps(method)
    def answer(self: Any, *args: Any, **kwargs: Any) -> Any:
        value = method(self, *args, **kwargs)
        # A native answer short-circuits, which is both the common case (every
        # wrapper in `poop/types/` is written in Python) and what keeps this
        # importable: `bool(x)` runs during the package's own import, before
        # `_bridge` can be loaded.
        if isinstance(value, native):
            return value

        from poop.types._bridge import to_python

        raw = to_python(value)
        if isinstance(raw, native):
            return raw

        from poop.types._message import article
        from poop.types.exceptions import MIRRORS

        # Named by the role, never by the slot: a message spelling `__str__`
        # names the construct `no_dunder_attribute` bans — and CPython's own
        # sentence for this was `__str__ returned non-string (type str)`,
        # which calls `str` the thing that is not a `str`.
        raise MIRRORS["TypeError"](
            f"{type(self).__name__}'s {role} must be "
            f"{article(spelling)}, got {article(type(value).__name__)}"
        )

    return answer


def _length_message(self: Any) -> Any:
    """`len` for a class that declared `__len__` and no message to ask with."""
    from poop.types.int import Int

    return Int(builtins.len(self))


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

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        /,
        **kwargs: Any,
    ) -> Any:
        """Build the class, adapting the protocol slots it declares.

        A POOP program may define `__str__`, `__repr__`, `__bool__`,
        `__hash__` and `__len__` — that is how an object says how it prints,
        compares or measures — but it can only *return* POOP values, and
        CPython reads these slots itself and demands a native. Every one of
        them was therefore impossible to satisfy from inside the language.
        The answer is unwrapped here, once, where the class is built.

        A class that declares `__len__` and no `len` also gets the message
        for it: `len` is how POOP asks, `no_len` names it as the substitute
        for the builtin, and a slot that raises nothing and answers nothing
        is the quiet member of the same family.

        The four parameters are positional-only: a class keyword is passed
        through here on its way to `__init_subclass__`, and
        `class ListIterator(..., name="list_iterator")` would otherwise
        collide with this signature's own `name`.
        """
        for slot in _PROTOCOL_SLOTS:
            method = namespace.get(slot)
            if callable(method):
                namespace[slot] = _adapted(slot, method)
        if callable(namespace.get("__len__")) and "len" not in namespace:
            namespace["len"] = _length_message
        return super().__new__(mcls, name, bases, namespace, **kwargs)

    @class_side
    def name(cls) -> Str:
        from poop.types.string import Str

        return Str(cls.__name__)

    @class_side
    def superclass(cls) -> Any:
        from poop.types._alias import unalias
        from poop.types.none import none

        # Smalltalk answers nil for Object superclass, which is also how the
        # raw Python `object` at the root stays out of reach.
        bases = [base for base in cls.__bases__ if isinstance(base, PoopMeta)]
        if not bases:
            return none
        first = bases[0]
        # An alias's one base is the wrapper it stands for, and both are
        # cloaked under the builtin's name — so climbing from a bare builtin
        # name met a rung that is not there: `int.superclass()` answered a
        # class calling itself `int`, which `is_identical(int)` then denied,
        # and `object` was two steps up instead of one. The pair is one class
        # as far as a program can tell, which is the decision `__eq__` below
        # already makes; the ladder says the same thing by stepping over it.
        if first is unalias(cls):
            return first.superclass()
        return first

    def __eq__(cls, other: object) -> Boolean:
        """Compare two classes, answering a `Boolean` like every other `==`.

        `Object.__eq__` answers a POOP object, but a *class* is compared by
        its metaclass, and nothing here defined the message — so `int == int`
        fell through to `type.__eq__` and handed a raw Python `bool` back to
        user code, which then answered `'bool' object has no attribute
        'print'`: CPython's vocabulary for the thing POOP calls a message,
        reached by the shortest program that compares two classes.

        `unalias` on both sides, so the two spellings of one class are one
        class. `class_()` answers the wrapper while a bare builtin name
        answers the `_alias.py` subclass of it, so `(5).class_() == int` was
        `False` for a program that is right — silently, and about two objects
        that both call themselves `int`. `is_identical` deliberately does not
        follow: it asks identity, and those really are two objects.
        """
        from poop.types._alias import unalias
        from poop.types.boolean import to_boolean

        return to_boolean(unalias(cls) is unalias(other))

    def __ne__(cls, other: object) -> Boolean:
        from poop.types._alias import unalias
        from poop.types.boolean import false, true

        return false if unalias(cls) is unalias(other) else true

    # Defining `__eq__` sets `__hash__` to None, which would make every POOP
    # class unhashable — `NATIVE_TO_POOP` keys on classes, and so does every
    # `type` CPython puts in a set or dict. Identity hashing is also what
    # keeps the `__eq__` above consistent for the classes it does *not*
    # unalias: two distinct classes stay distinct in both.
    __hash__ = type.__hash__

    @class_side_refusal
    def mro(cls) -> Any:
        """Refuse `type.mro` — `superclass` is the question POOP answers.

        Inherited from the metaclass, it answered a raw Python list of raw
        classes: `__mro__` under a spelling `no_dunder_attribute` cannot see,
        holding the Python `object` that `superclass` stops short of on
        purpose. `dir()` never listed it either, so it was unreachable by
        reading and reachable by typing.

        CPython calls this method to *compute* a new class's MRO — `mro_invoke`
        consults the metaclass whenever it is not plain `type` — so refusing
        unconditionally breaks every `class` statement in the language. During
        that call the class has no `__mro__` yet; once it does, the caller is a
        program rather than the interpreter, and that is the line drawn here.
        """
        if getattr(cls, "__mro__", None) is None:
            return type.mro(cls)
        _refuse_native(cls, "mro", "superclass")

    @class_side_refusal
    def register(cls, subclass: Any) -> Any:
        """Refuse `ABCMeta.register` — inheritance is how POOP says "is a".

        Virtual-subclass registration makes `is_instance` and `is_subclass`
        answer true for a class that never inherited from the receiver, moving
        the answer into a side table no reader of the class can see.
        """
        _refuse_native(cls, "register", "is_subclass")

    @class_side_refusal
    def raise_(cls, *args: Any, **kwargs: Any) -> Never:
        """Refuse `raise_` on a class that is not an error.

        The message itself lives on `PoopExcMeta`, so every mirror and every
        user class descending from one answers it — and nothing else does.
        Without this twin the non-exception case reported the *constructor* of
        a class the program never asked to build: `A.raise_("x")` answered
        `A() takes no arguments`, which the parse-time rewrite produced for any
        capitalized receiver it saw.
        """
        from poop.types.object import MessageNotUnderstood

        raise MessageNotUnderstood(
            f"{cls.__name__} cannot be raised — "
            "only a class descending from Exception can",
            name="raise_",
            obj=cls,
        )

    @class_side
    def has_attr(cls, name: Str) -> Boolean:
        from poop.types.boolean import to_boolean

        raw = _checked_name(name)
        try:
            _reflected(cls, raw)
        except AttributeError:
            return to_boolean(False)
        return to_boolean(True)

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

    if not TYPE_CHECKING:
        # Hidden from the type checker for the reason `__getattr__` below and
        # `Object.__getattr__` both give: a visible hook answers `Any` for
        # every name, so `Foo.frobnicate()` would type-check on every POOP
        # class and `ty` would stop catching typos across the codebase.
        def __getattribute__(cls, name: str) -> Any:
            """A method the instance answers is refused, not bound and handed out.

            `type.__getattribute__` hands a plain function back unbound, so
            every wrapper message reached through the class answered CPython's
            binding error — `str.upper() missing 1 required positional
            argument: 'self'`. See `_refuse_instance_side`. Narrow on purpose:
            only a plain `FunctionType` found on the class's own MRO, so
            `super().m()`, `classmethod`, `staticmethod`, `property`,
            `class_side` and the metaclass's own messages all resolve exactly
            as before. `_`-prefixed names are left alone, as `is_message`
            already draws that boundary and the interpreter reads `__mro__`,
            `__slots__` and the rest through it.
            """
            value = type.__getattribute__(cls, name)
            # Two tests, cheapest first. `FunctionType` alone is not enough:
            # `staticmethod.__get__` answers the *wrapped function*, so a
            # `@staticmethod` — the one shape `no_class_machinery` leaves open
            # and `examples/patterns/execute_around.py` is built on — looked
            # exactly like an instance method here. `_instance_only` reads the
            # MRO's dicts, where the wrapper is still visible.
            if (
                type(value) is FunctionType
                and not name.startswith("_")
                and _instance_only(cls, name)
            ):
                _refuse_instance_side(cls, name)
            return value

    def __dir__(cls) -> list[str]:
        """Merge the class side into `dir(cls)`, minus the refusals.

        CPython's `type.__dir__` walks the class's *own* MRO only, so none of
        the messages that live on the metaclass appeared in any discovery
        surface: `Foo.dir()` answered no `name` and no `superclass`, and
        `ValueError.dir()` no `raise_` — a documented protocol reachable only
        by typing it. The other class-side messages were already listed, but
        for the instance-side reason: `Object` happens to spell them the same.

        Answered here rather than in `dir` below, because `dir` is not the only
        reader: `:methods`, the REPL completer and the near-miss hint all call
        Python's `dir`, and each would have needed its own copy of the merge.

        A refusing descriptor is left out — offering a name that answers "that
        is Python's, use #superclass" teaches worse than not offering it at
        all. The same rule now covers the instance-only half: this list used to
        merge two receivers' messages under a header claiming one, so
        `:methods str` said `str understands 90 messages` and 64 of them
        answered a binding error. `class_` and `class_name` go with them —
        `Object` answers both, but the class refuses them, and this is a list
        of what *this* receiver understands.
        """
        answers: dict[str, bool] = {}
        for metaclass in type(cls).__mro__:
            for name, attr in vars(metaclass).items():
                if isinstance(attr, class_side):
                    # First in the metaclass MRO wins, as attribute lookup
                    # itself resolves: `PoopExcMeta.raise_` is a message, and
                    # `PoopMeta.raise_` below it is the refusing twin.
                    answers.setdefault(name, not attr.refuses)
        merged = {name for name, answered in answers.items() if answered}
        own = {name for name in super().__dir__() if not _instance_only(cls, name)}
        # A set: the builtin `dir` sorts what it is handed but does not dedupe
        # — `type.__dir__` does that internally, and this merge reaches past
        # it, so every name `Object` also spells (`print`, `hash`, …) came back
        # twice and `:methods` counted 51 messages on a class that has 30.
        # The union is what puts those back: `print` is a plain method on
        # `Object` *and* a `class_side` message, so it is dropped by the filter
        # and restored by the merge, which is exactly the two-receiver
        # distinction the filter exists to draw.
        return sorted(own | merged)

    @class_side
    def dir(cls) -> List:
        from poop.types._selectors import is_message
        from poop.types.list import List
        from poop.types.string import Str

        # Mirror `Object.dir`: hide every `_`-prefixed name so the class side
        # never leaks dunders or the mangled `_poop_*` internals. `is_message`
        # is the one copy of that rule, shared with `Object.dir` and the REPL.
        return List(*(Str(name) for name in builtins_dir(cls) if is_message(name)))

    @class_side
    def format(cls, spec: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap
        from poop.types.string import Str

        return Str(builtins_format(cls.__name__, _unwrap(spec, "")))

    @class_side_refusal
    def class_(cls) -> Any:
        # Smalltalk answers the metaclass here — `Foo class` is `Foo class`.
        # POOP has none to answer with: `PoopMeta` is not itself a POOP class
        # (`type(PoopMeta)` is `type`), so handing it back would leak exactly
        # the raw class object the class side exists to remove. Refusing and
        # naming `name` teaches; answering `Foo` would quietly make
        # `class_name` mean one thing on an instance and another on a class.
        _refuse(cls, "class_")

    @class_side_refusal
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
        from poop.types._alias import unalias
        from poop.types._argument import a_class
        from poop.types.boolean import to_boolean

        # A class is an instance of its metaclass, not of its own bases, so
        # `Foo.is_instance(Object)` is `false` — `Foo.is_subclass(Object)` is
        # the "descends from" question. `unalias` for the reason
        # `Object.is_instance` gives.
        return to_boolean(isinstance(cls, a_class(unalias(type_), "is_instance")))

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
        raw = _checked_name(name)
        try:
            return _as_block(_reflected(cls, raw))
        except AttributeError:
            if default:
                return default[0]
            return cls.does_not_understand(raw)

    @class_side
    def set_attr(cls, name: Str, value: Any) -> NoneClass:
        from poop.types.none import none

        # Name first, receiver second: a forbidden *name* is refused by name
        # on every receiver, so `str.set_attr("__dict__", …)` still answers
        # the dunder ban rather than the builtin one.
        raw = _checked_name(name)
        _reject_builtin(cls)
        builtins.setattr(cls, raw, value)
        return none

    @class_side
    def del_attr(cls, name: Str) -> NoneClass:
        from poop.types.none import none

        raw = _checked_name(name)
        _reject_builtin(cls)
        builtins.delattr(cls, raw)
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
            # The instance-side refusal lands here, not where it was raised:
            # `MessageNotUnderstood` is an `AttributeError` on purpose, so
            # `__getattribute__` failing sends Python straight to this hook,
            # which would replace the sentence with the generic near-miss one.
            # Asking the same question again is what keeps the teaching half.
            if _instance_only(cls, name):
                _refuse_instance_side(cls, name)
            return cls.does_not_understand(name)
