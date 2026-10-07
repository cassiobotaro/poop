from poop.transformers._collection import make_bytes_from
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.byte_array import ByteArray

_poop_bytearray_from = make_bytes_from(
    ByteArray,
    lambda raw: ByteArray(bytearray(raw)),
    hint='write bytearray(b"…") to copy bytes',
    copy=True,
)


class _ByteArrayRewriter(BuiltinRewriter):
    builtin = "bytearray"
    call_target = "_poop_bytearray_from"
    name_target = "_poop_bytearray_cls"


class ByteArrayTransformer(BaseTransformer):
    rewriter = _ByteArrayRewriter
    BINDINGS = {
        "_poop_bytearray": ByteArray,
        "_poop_bytearray_cls": builtin_alias(
            ByteArray, _poop_bytearray_from, "bytearray"
        ),
        "_poop_bytearray_from": _poop_bytearray_from,
    }
