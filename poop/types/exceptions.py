"""POOP's exception hierarchy — the class side of `Try` and `raise_`.

`Try.except_(ValueError, handler)` and `ValueError.raise_("msg")` used to take a
native CPython class, the last raw primitive in POOP's own substitutes for two
forbidden constructs. `INFECTIONS.md` justified it with "mirroring Python's full
hierarchy (~100+ classes) is impractical"; Python 3.14 has 71 builtin
exceptions, and a language with no files and no modules cannot reach the
`OSError` subtree. What it can reach is the table below.

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

`MIRRORS` is also how POOP raises its *own* diagnostics. A wrapper composing a
POOP message used to carry it on a native class — POOP's advice labelled with
Python's vocabulary — and nothing stopped the next one from doing the same. The
rule is now one line: inside `poop/types/` and `poop/transformers/`, a failure a
program can reach is raised as `MIRRORS[...]`, never as the bare builtin.
Subclassing keeps it catchable by anything that caught the native, so the rule
costs nothing; `tests/test_mirrored_raises.py` sweeps both packages for it.
"""

from __future__ import annotations

from typing import Any, Never, cast

from poop.types.meta import PoopMeta, class_side, class_side_read_refusal
from poop.types.object import Object


class PoopExcMeta(PoopMeta):
    """Matches a POOP exception class against the native one it mirrors."""

    @class_side
    def raise_(cls, *args: Any, **kwargs: Any) -> Never:
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

    def __instancecheck__(cls, obj: object) -> bool:
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


# (native class, the POOP parent's name) — mirrors Python's own tree, so
# `except_(LookupError, ...)` catches a raw KeyError the way `except` does.
_HIERARCHY: tuple[tuple[type[BaseException], str | None], ...] = (
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

# Annotated as exception classes, not bare `type`: every POOP diagnostic is
# raised through this table (`raise MIRRORS["TypeError"](...)`), so the values
# have to be raisable to the type checker as well as at runtime.
MIRRORS: dict[str, type[Exception]] = {}
NATIVE_TO_POOP: dict[type[BaseException], type] = {}


# Names a mirror inherits from `BaseException` that POOP never designed, mapped
# to the message a reader wanted instead — `None` where there is none.
#
# `PoopMeta` already refuses `type.mro` and `ABCMeta.register` for exactly this
# reason, and `INFECTIONS.md` describes those two as "unreachable by reading and
# reachable by typing". These are worse: `dir` *did* list them, so `:methods
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
    from poop.types.object import MessageNotUnderstood

    tail = (
        f"a caught error answers #{instead}"
        if instead is not None
        else "POOP does not offer it"
    )
    raise MessageNotUnderstood(
        f"{cls.__name__} does not understand #{name} — #{name} is Python's; {tail}",
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
            from poop.types._selectors import explain
            from poop.types.object import MessageNotUnderstood

            raise MessageNotUnderstood(
                explain(cls, name, cls.__name__), name=name, obj=cls
            )
        return _refuse_python_attribute(cls, name, instead)

    refuse.__name__ = name
    refuse.__qualname__ = name
    return class_side_read_refusal(cast("Any", refuse), refuses=True)


def _build(native: type[BaseException], parent: str | None) -> None:
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
        "type[Exception]",
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
            },
        ),
    )
    MIRRORS[native.__name__] = mirror
    NATIVE_TO_POOP[native] = mirror


for _name, _instead in _PYTHON_ATTRIBUTES.items():
    setattr(PoopExcMeta, _name, _refusal_for(_name, _instead))
    # `__set_name__` is only called for descriptors written in a class body, and
    # these are installed after `PoopExcMeta` is built — so `cloak_callable`
    # never ran on them and `_name` stayed empty, which `__set__` reads when it
    # refuses a rebind.
    _refusal = vars(PoopExcMeta)[_name]
    _refusal.__set_name__(PoopExcMeta, _name)


for _native, _parent in _HIERARCHY:
    _build(_native, _parent)


def poop_class_of(exc: BaseException) -> Any:
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
