from collections.abc import Iterable
from typing import ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.string import Str


def _poop_bytearray_from(*args: object, **kwargs: object) -> ByteArray:
    """`bytearray()`, `bytearray(source)` and `bytearray(text, encoding)`.

    The text form is here because `Bytes` and `ByteArray` mirror each other
    message for message, and this was the one half-pair — `most=1` refused
    `bytearray("ab", "utf-8")`, legal Python, and the one-argument spelling
    fell through the `Iterable` branch to `bytearray(<str chars>)`, answering
    `'str' object cannot be interpreted as an integer`: a message about
    integers, for an argument that is text. It delegates through `Str.encode`
    for the reason `_poop_bytes_from` gives at length.
    """
    refuse_extra_arguments(
        "bytearray",
        args,
        kwargs,
        most=3,
        built_from="at most one source, plus an encoding and errors for text",
        hint='write bytearray(b"…") to copy bytes',
    )
    arg = args[0] if args else None
    codec = cast("tuple[Str, ...]", args[1:])
    if isinstance(arg, Str):
        if not codec:
            raise MIRRORS["TypeError"]("string argument without an encoding")
        return ByteArray(arg.encode(*codec)._value)
    if codec:
        raise MIRRORS["TypeError"]("encoding without a string argument")
    if arg is None:
        return ByteArray()
    if isinstance(arg, Bytes):
        return ByteArray(arg._value)
    if isinstance(arg, Int):
        return ByteArray(bytearray(arg._value))
    if isinstance(arg, Iterable):
        ints = cast("Iterable[Int]", arg)
        return ByteArray(item._value for item in ints)
    raise MIRRORS["TypeError"](f"cannot convert {type(arg).__qualname__} to bytearray")


class _ByteArrayRewriter(BuiltinRewriter):
    builtin = "bytearray"
    call_target = "_poop_bytearray_from"
    name_target = "_poop_bytearray_cls"


class ByteArrayTransformer(BaseTransformer):
    rewriter = _ByteArrayRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_bytearray": ByteArray,
        "_poop_bytearray_cls": builtin_alias(
            ByteArray, _poop_bytearray_from, "bytearray"
        ),
        "_poop_bytearray_from": _poop_bytearray_from,
    }
