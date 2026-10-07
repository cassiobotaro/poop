from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.boolean import Boolean
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _poop_float_from(*args: object, **kwargs: object) -> Float:
    refuse_extra_arguments(
        "float",
        args,
        kwargs,
        most=1,
        built_from="at most one number or string",
        hint="write a literal for a value",
    )
    value = args[0] if args else None
    if value is None:
        return Float(0.0)
    if isinstance(value, Float):
        return value
    if isinstance(value, Boolean):
        # CPython's float(True) -> 1.0 / float(False) -> 0.0.
        return Float(1.0 if bool(value) else 0.0)
    if isinstance(value, Int):
        return Float(float(value._value))
    if isinstance(value, Str):
        try:
            return Float(float(value._value))
        except ValueError:
            # `could not convert string to float: 'abc'` names Python's type,
            # not the message the reader sent.
            raise MIRRORS["ValueError"](
                f"{value._value!r} is not a valid float"
            ) from None
    raise MIRRORS["TypeError"](f"cannot convert {type(value).__name__} to float")


class _FloatRewriter(BuiltinRewriter):
    builtin = "float"
    call_target = "_poop_float_from"
    name_target = "_poop_float_cls"
    literal_type = float
    literal_target = "_poop_float"


class FloatTransformer(BaseTransformer):
    rewriter = _FloatRewriter
    BINDINGS = {
        "_poop_float": Float,
        "_poop_float_cls": builtin_alias(Float, _poop_float_from, "float"),
        "_poop_float_from": _poop_float_from,
    }
