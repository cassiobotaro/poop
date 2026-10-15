"""POOP's exception hierarchy — the class side of `Try` and `raise_`.

`Try.except_(ValueError, handler)` and `ValueError.raise_("msg")` used to take a
native CPython class, the last raw primitive in POOP's own substitutes for two
forbidden constructs. `INFECTIONS.md` justified it with "mirroring Python's full
hierarchy (~100+ classes) is impractical"; Python 3.15 has 72 builtin
exceptions, and a language with no files and no modules cannot reach the
`OSError` subtree, nor `ImportCycleError`, the one 3.15 added under
`ImportError`. What it can reach is the table below.

The `Unicode*` family is reachable — `encode`/`decode` can fail on the text
they are handed — and is deliberately *not* mirrored: `_codec.py` rewords both
failures as a `ValueError`, which is what `UnicodeError` is in CPython's tree,
rather than reproducing a five-argument constructor whose `__str__` composes
the `codec` sentence that module exists to keep out.

No translation layer is needed, which is what makes this cheap: `Try._execute()`
catches `except BaseException` and then matches with `isinstance()` — POOP's own
code, never a Python `except` clause — so a metaclass `__instancecheck__` is
enough for a POOP class to match its native twin. The mirrors subclass that twin
so they stay raisable, which is what `raise_` depends on.

The mirrors are also how POOP raises its *own* diagnostics. A wrapper
composing a POOP message used to carry it on a native class — POOP's advice
labelled with Python's vocabulary — and nothing stopped the next one from doing
the same. The rule is now one line: inside `poop/types/` and
`poop/transformers/`, a failure a program can reach is raised as
`mirrors.TypeError(...)` — each mirror under its own name in `mirrors.py` —
never as the bare builtin. Subclassing keeps it catchable by anything that
caught the native, so the rule costs nothing; `tests/test_mirrored_raises.py`
sweeps both packages for it.
"""

import builtins
from typing import TYPE_CHECKING, Literal, Never, cast, get_args

from poop.types._cloak import cloak, cloak_callable
from poop.types._message import poop_message
from poop.types._selectors import explain, is_dunder, is_message, not_understood
from poop.types.meta import PoopMeta, class_side, class_side_read_refusal
from poop.types.object import MessageNotUnderstood, Object

# circular: each module below imports exceptions
lazy from poop.types._unwrap import _unwrap, _unwrap_bool
lazy from poop.types.none import none
lazy from poop.types.string import Str


class PoopExcMeta(PoopMeta):
    """Matches a POOP exception class against the native one it mirrors."""

    @class_side
    def raise_(cls, *args: object, **kwargs: object) -> Never:  # noqa: N805 — a class-side message
        """Signal this error — POOP's substitute for the `raise` statement.

        A real class-side message, not a parse-time rewrite. `RaiseTransformer`
        matched a literal uppercase `ast.Name` followed by `.raise_(...)`, so
        every other way of naming the same class failed — and failed by saying
        something untrue about the object: a class bound to a lowercase name,
        one read out of a collection, and `e.kind()` inside a handler all
        answered `ValueError does not understand #raise_`. The last made a
        *re-raise* inexpressible, since `Try` swallows a matched exception and
        `raise` is banned. Nothing defined `raise_` anywhere either, so `dir()`
        did not list it and `:methods` could not show the substitute
        `no_raise` names.

        Everything the rewrite bought is kept: this is an expression, so it
        still works inside a `lambda`, and `**kwargs` still ride along to an
        exception whose fields arrive by keyword.
        """
        raise cls(*args, **kwargs)

    def __instancecheck__(cls, obj: object) -> bool:  # noqa: N805 — a metaclass method
        # `_native` is read from the class's own __dict__, never inherited: a
        # user's `class MyError(Exception)` would otherwise inherit the root's
        # `_native = Exception` and catch every exception in the program —
        # silent and total. Falling back to normal behaviour makes a user
        # subclass match itself. The obvious alternative, an __init_subclass__
        # setting `_native = cls`, recurses forever: __instancecheck__ would
        # call itself.
        native = cls.__dict__.get("_native")
        if native is None:
            return super().__instancecheck__(obj)
        return isinstance(obj, native)


# The keys `MIRRORS` answers, spelt out so a type checker can hold them: the
# table-shaped readers (`poop_class_of`, the `_at.py` helpers) look a mirror up
# by name, and as a `dict[str, …]` a mistyped key passed every check and failed
# as a `KeyError` on the error path itself — the least-exercised code there is. `test_mirror_names_match_the_hierarchy` keeps
# this from becoming a second list to keep in step with `_HIERARCHY` by hand.
type MirrorName = Literal[
    "Exception",
    "ArithmeticError",
    "LookupError",
    "ZeroDivisionError",
    "OverflowError",
    "IndexError",
    "KeyError",
    "AttributeError",
    "NameError",
    "TypeError",
    "ValueError",
    "RuntimeError",
    "NotImplementedError",
    "RecursionError",
    "AssertionError",
    "StopIteration",
    "EOFError",
]
MIRROR_NAMES: tuple[MirrorName, ...] = get_args(MirrorName.__value__)

# (native class, the POOP parent's name) — mirrors Python's own tree, so
# `except_(LookupError, ...)` catches a raw KeyError the way `except` does.
_HIERARCHY: tuple[tuple[type[BaseException], MirrorName | None], ...] = (
    (Exception, None),
    (ArithmeticError, "Exception"),
    (LookupError, "Exception"),
    (ZeroDivisionError, "ArithmeticError"),
    (OverflowError, "ArithmeticError"),
    (IndexError, "LookupError"),
    (KeyError, "LookupError"),
    (AttributeError, "Exception"),
    (NameError, "Exception"),
    (TypeError, "Exception"),
    (ValueError, "Exception"),
    (RuntimeError, "Exception"),
    (NotImplementedError, "RuntimeError"),
    # Recursion is POOP's substitute for every loop, so this is the most
    # reachable of the lot rather than an exotic one.
    (RecursionError, "RuntimeError"),
    (AssertionError, "Exception"),
    (StopIteration, "Exception"),
    # `Str.input` is the one message that reads from outside the program, and
    # end-of-input is the one failure it has. Without a mirror a program could
    # not name what it was catching: `except_(EOFError, …)` answered `name
    # 'EOFError' is not defined`, and `except_(Exception, …)` reported the
    # kind as `Exception`, so the only I/O POOP has was also the only failure
    # it could not handle by name.
    (EOFError, "Exception"),
)

if TYPE_CHECKING:
    from types import FunctionType

    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass

    # The shape of a mirror, for the checker alone: an exception class whose
    # metaclass is `PoopExcMeta`. Every POOP diagnostic is raised through the
    # table (`raise MIRRORS["TypeError"](...)`), so the values have to be
    # raisable, and `e.kind().name()` sends a class-side message to one, so
    # they have to answer the class side too. `_build` makes each one from
    # the metaclass by hand, which is why the shape is stated here rather than
    # by a class statement.
    class Mirror(Exception, Object, metaclass=PoopExcMeta): ...


MIRRORS: dict[MirrorName, type[Mirror]] = {}
NATIVE_TO_POOP: dict[type[BaseException], type[Mirror]] = {}


# Names a mirror inherits from `BaseException` that POOP never designed, mapped
# to the message a reader wanted instead — `None` where there is none.
#
# `PoopMeta` already refuses `type.mro` for exactly this reason, and
# `INFECTIONS.md` describes it as "unreachable by reading and reachable by
# typing". These are worse: `dir` *did* list them, so `:methods
# ValueError` advertised them, and what they answered said they were not POOP's
# — `args` a raw Python tuple, `with_traceback` a raw method descriptor, and
# `add_note` a refusal naming `BaseException` and a `'str' object` no program
# mentioned. The instance side already refused all of them, so the class
# advertised names the caught error would not answer.
#
# Every one of them is an attribute of an exception *instance* in CPython, which
# is why none means anything on the class — including `obj` and `value`, which
# only two natives carry and which are therefore installed only where they exist.
_PYTHON_ATTRIBUTES: dict[str, str | None] = {
    "args": "message",
    "add_note": None,
    "with_traceback": None,
    "obj": None,
    "value": None,
}


def _refuse_python_attribute(cls: type, name: str, instead: str | None) -> Never:
    """Refuse a name a mirror inherited from `BaseException`.

    The shape `_refuse_native` uses for `mro` and `register`, with the pointer
    aimed one receiver over: these are instance attributes, so the message a
    reader wanted is answered by the *caught error*, not by the class.
    """
    tail = (
        f"a caught error answers #{instead}"
        if instead is not None
        else "POOP does not offer it"
    )
    raise MessageNotUnderstood(
        not_understood(cls.__name__, name, f"#{name} is Python's; {tail}"),
        name=name,
        obj=cls,
    )


def _refusal_for(name: str, instead: str | None) -> class_side:
    """A read-refusing class-side descriptor for one inherited name.

    Read-refusing rather than call-refusing because every name here is an
    *attribute*: `ValueError.args` carries no parentheses, so a refusal that
    waits for a call would hand back the descriptor instead. `add_note` and
    `with_traceback` are callables in CPython, but refusing them a step earlier
    is what a reader wants — the message is about the name, not the call.

    Installed on `PoopExcMeta`, which is where a `class_side` descriptor has to
    live: a class body's own descriptor is invoked as `__get__(None, owner)` and
    would answer itself, and `__dir__` filters the metaclass. `obj` and `value`
    ride along even though only two natives carry them, so the refusal asks the
    native before claiming a name is Python's — `AttributeError.obj` names why,
    and `ValueError.obj` keeps the plain "does not understand" that is the truth
    for it.
    """

    def refuse(cls: type) -> Never:
        native = getattr(cls, "_native", None)
        if native is None or not hasattr(native, name):
            raise MessageNotUnderstood(
                explain(cls, name, cls.__name__), name=name, obj=cls
            )
        return _refuse_python_attribute(cls, name, instead)

    return class_side_read_refusal(refuse, refuses=True)


def describe(exc: BaseException) -> str:
    """`<Kind>: <message>`, or the bare kind when the message is empty.

    The one composition of an exception's displayed form: the executor's
    uncaught report, a caught `Error`'s `__str__` and an exception instance a
    program built all show the same text. The kind is `poop_class_of`'s, so it
    is always one a program can write and always the one a handler is given.
    """
    name = poop_class_of(exc).__name__
    message = poop_message(exc)
    return f"{name}: {message}" if message else name


# The instance side of the root mirror. An exception a program *built* —
# `ValueError("x")`, or an instance of its own `class Field(Exception)` — is a
# POOP object by descent and answered none of what a *caught* `Error` answers:
# no `message`, no `kind`, and `raise_()` refused as a class-side message, so
# a pre-built exception could not be raised at all. Meanwhile `args`,
# `add_note` and `with_traceback` resolved through `BaseException` and
# answered natives, the refusals in `_PYTHON_ATTRIBUTES` being installed on
# the metaclass, which instance lookup never consults.
#
# `__str__` is left to `Exception.__str__` on purpose: it is what
# `poop_message` reads, what CPython's own traceback prints, and what a
# program's `__str__` override replaces. `print` and `__repr__` compose the
# displayed form from it instead, through `describe`.


def _message(self: BaseException) -> Str:
    return Str(poop_message(self))


def _kind(self: BaseException) -> PoopExcMeta:
    return poop_class_of(self)


def _raise(self: BaseException) -> Never:
    raise self


def _print(
    self: BaseException,
    end: Str | NoneClass | None = None,
    flush: Boolean | NoneClass | None = None,
) -> NoneClass:
    # `Object.print` on the described form rather than on `str(self)`, which
    # is the bare message and has to stay so.
    builtins.print(  # noqa: T201
        describe(self), end=_unwrap(end, "\n"), flush=_unwrap_bool(flush, False)
    )
    return none


def _repr(self: BaseException) -> str:
    return describe(self)


def _is_refused_native(self: BaseException, name: str) -> bool:
    """Whether `name` is a `BaseException` attribute this instance refuses."""
    native = getattr(type(self), "_native", None)
    return name in _PYTHON_ATTRIBUTES and native is not None and hasattr(native, name)


def _getattribute(self: BaseException, name: str) -> object:
    if _is_refused_native(self, name):
        _refuse_python_attribute(type(self), name, _PYTHON_ATTRIBUTES[name])
    return Object.__getattribute__(self, name)


def _getattr(self: BaseException, name: str) -> object:
    # `Object.__getattr__`, re-asking first: the refusal above is an
    # `AttributeError`, so Python answers it by calling this hook, which would
    # otherwise replace the sentence with the generic near-miss one — the
    # detour `PoopMeta.__getattr__` documents. The dunder probe is refused on
    # the mirror rather than natively, since the table is built by the time an
    # instance exists.
    if _is_refused_native(self, name):
        _refuse_python_attribute(type(self), name, _PYTHON_ATTRIBUTES[name])
    if is_dunder(name):
        raise MIRRORS["AttributeError"](name)
    return cast("Object", self).does_not_understand(Str(name))


def _dir(self: BaseException) -> list[str]:
    # What `Object.dir` lists, minus the names the guard above refuses:
    # advertising `args` and then refusing it was the class side's bug.
    return [
        name
        for name in object.__dir__(self)
        if not (is_message(name) and name in _PYTHON_ATTRIBUTES)
    ]


_INSTANCE_SIDE: dict[str, object] = {
    "message": _message,
    "kind": _kind,
    "raise_": _raise,
    "print": _print,
    "__repr__": _repr,
    "__getattribute__": _getattribute,
    "__getattr__": _getattr,
    "__dir__": _dir,
}

# Under the message each answers: a wrong-arity call is reported from the
# function's name, and `cloak` below prefixes it with the class's.
for _key, _fn in _INSTANCE_SIDE.items():
    cloak_callable(cast("FunctionType", _fn), _key)


def _build(native: type[BaseException], parent: MirrorName | None) -> None:
    # The root also inherits Object, so a user's `class MyError(Exception)`
    # lands inside the Object tree and answers print()/class_name() — before
    # this it sat outside it entirely.
    bases: tuple[type, ...] = (
        (MIRRORS[parent], native) if parent is not None else (Exception, Object)
    )
    # Cast, not a wider annotation: a metaclass call answers `PoopExcMeta`, and
    # only the bases say the result is an exception class. Every branch above
    # puts a native exception in `bases`, so the claim holds.
    mirror = cast(
        "type[Mirror]",
        PoopExcMeta(
            native.__name__,
            bases,
            {
                "_native": native,
                "__module__": "builtins",
                "__slots__": (),
                # A no-op for every mirror but `KeyError`, whose `__str__`
                # answers `repr(args[0])` — so a POOP sentence handed to it
                # came back wrapped in Python's quotes: `"dict has no key
                # 'b'"`. The missing key's own repr is the message's to
                # compose, not the exception class's to add.
                "__str__": Exception.__str__,
                **(_INSTANCE_SIDE if parent is None else {}),
            },
        ),
    )
    # The mirrors are built by hand rather than through `Object.__init_subclass__`'s
    # `name=` keyword, so the cloak that names a class's own functions after it
    # is applied here; it only has anything to rename on the root.
    cloak(mirror, native.__name__)
    MIRRORS[cast("MirrorName", native.__name__)] = mirror
    NATIVE_TO_POOP[native] = mirror


def _install_refusals() -> None:
    for name, instead in _PYTHON_ATTRIBUTES.items():
        refusal = _refusal_for(name, instead)
        # `__set_name__` is only called for descriptors written in a class body,
        # and these are installed after `PoopExcMeta` is built — so it is called
        # here: it names the function through `cloak_callable` and fills
        # `_name`, which `__set__` reads when it refuses a rebind.
        refusal.__set_name__(PoopExcMeta, name)
        setattr(PoopExcMeta, name, refusal)


def _build_mirrors() -> None:
    for native, parent in _HIERARCHY:
        _build(native, parent)


_install_refusals()
_build_mirrors()


def poop_class_of(exc: BaseException) -> PoopExcMeta:
    """The POOP class answering for `exc` — its mirror, or the nearest one.

    A user's own exception is already a POOP class and answers for itself. An
    unmirrored native (`MemoryError`, say) answers with the closest mirrored
    ancestor rather than leaking the raw class back out.
    """
    for base in type(exc).__mro__:
        if isinstance(base, PoopExcMeta):
            return base
        mirror = NATIVE_TO_POOP.get(base)
        if mirror is not None:
            return mirror
    return MIRRORS["Exception"]
