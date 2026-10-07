from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.memory_view import MemoryView


def _poop_memoryview_from(*args: object, **kwargs: object) -> MemoryView:
    refuse_extra_arguments(
        "memoryview",
        args,
        kwargs,
        most=1,
        built_from="exactly one bytes-like object",
        hint="write memoryview(b) over the buffer you mean",
    )
    arg = args[0] if args else None
    if isinstance(arg, Bytes | ByteArray):
        return MemoryView(memoryview(arg._value))
    raise MIRRORS["TypeError"](
        f"memoryview: a bytes-like object is required, not {type(arg).__qualname__}"
    )


class _MemoryViewRewriter(BuiltinRewriter):
    builtin = "memoryview"
    call_target = "_poop_memoryview_from"
    name_target = "_poop_memoryview_cls"


class MemoryViewTransformer(BaseTransformer):
    rewriter = _MemoryViewRewriter
    BINDINGS = {
        "_poop_memoryview": MemoryView,
        "_poop_memoryview_cls": builtin_alias(
            MemoryView, _poop_memoryview_from, "memoryview"
        ),
        "_poop_memoryview_from": _poop_memoryview_from,
    }
