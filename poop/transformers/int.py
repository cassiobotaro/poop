from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.boolean import Boolean
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _parsed(value: Str, base: int | None) -> Int:
    """`int(text)` / `int(text, base)`, reworded.

    CPython answers `invalid literal for int() with base 10: 'abc'` — a Python
    call, plus a base the reader never passed — and `int() base must be >= 2
    and <= 36, or 0`, naming the same call again.

    The base is checked here rather than read back out of CPython's message:
    that message says `base` too, so telling the two failures apart by their
    text would have made `int("abc")` answer the base's error.
    """
    if base is not None and base != 0 and not 2 <= base <= 36:
        raise MIRRORS["ValueError"]("int base must be 0, or between 2 and 36")
    try:
        return Int(int(value._value, 10 if base is None else base))
    except ValueError:
        in_base = "" if base is None else f" in base {base}"
        raise MIRRORS["ValueError"](
            f"{value._value!r} is not a valid int{in_base}"
        ) from None


def _poop_int_from(*args: object, **kwargs: object) -> Int:
    refuse_extra_arguments(
        "int",
        args,
        kwargs,
        most=2,
        built_from="at most a value and a base",
        hint="write a literal for a value",
    )
    value = args[0] if args else None
    base = args[1] if len(args) > 1 else None
    if base is not None and not isinstance(value, Str):
        # Mirror CPython: a base is meaningful only when parsing a string.
        # int(10, 2) / int(3.5, 2) / int(True, 2) all raise TypeError there;
        # silently dropping the base would diverge from the language.
        raise MIRRORS["TypeError"]("a base applies only to text")
    if base is not None and not isinstance(base, Int):
        raise MIRRORS["TypeError"](f"base must be int, got {type(base).__name__}")
    match value:
        case None:
            return Int(0)
        case Int():
            return value
        case Boolean():
            # CPython's int(True) -> 1 / int(False) -> 0 (the flag-to-number
            # bridge). Boolean is kept out of *implicit* arithmetic, but
            # explicit conversion is sanctioned (like str(True)).
            return Int(1 if bool(value) else 0)
        case Float():
            return Int(int(value._value))
        case Str():
            return _parsed(value, None if base is None else base._value)
        case _:
            raise MIRRORS["TypeError"](f"cannot convert {type(value).__name__} to int")


class _IntRewriter(BuiltinRewriter):
    builtin = "int"
    call_target = "_poop_int_from"
    name_target = "_poop_int_cls"
    literal_type = int
    literal_target = "_poop_int"


class IntTransformer(BaseTransformer):
    rewriter = _IntRewriter
    BINDINGS = {
        "_poop_int": Int,
        "_poop_int_cls": builtin_alias(Int, _poop_int_from, "int"),
        "_poop_int_from": _poop_int_from,
    }
