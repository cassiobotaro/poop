from poop.transformers._collection import make_bytes_from
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.bytes import Bytes

_poop_bytes_from = make_bytes_from(
    Bytes,
    lambda raw: Bytes(bytes(raw)),
    hint='write a b"…" literal for bytes',
)


class _BytesRewriter(BuiltinRewriter):
    builtin = "bytes"
    call_target = "_poop_bytes_from"
    name_target = "_poop_bytes_cls"
    literal_type = bytes
    literal_target = "_poop_bytes"


class BytesTransformer(BaseTransformer):
    rewriter = _BytesRewriter
    BINDINGS = {
        "_poop_bytes": Bytes,
        "_poop_bytes_cls": builtin_alias(Bytes, _poop_bytes_from, "bytes"),
        "_poop_bytes_from": _poop_bytes_from,
    }
