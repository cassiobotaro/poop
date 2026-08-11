from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)
from builtins import (
    object as _object,  # preserve builtin before poop.transformers.object shadows it
)
from keyword import iskeyword as _iskeyword
from types import FunctionType as _FunctionType

from poop.transformers._collection import spread as _spread
from poop.transformers.base import BaseTransformer, Transformer
from poop.transformers.block import BlockTransformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.byte_array import ByteArrayTransformer
from poop.transformers.bytes import BytesTransformer
from poop.transformers.class_ import ClassTransformer
from poop.transformers.complex import ComplexTransformer
from poop.transformers.dict import DictTransformer
from poop.transformers.ellipsis import EllipsisTransformer
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.exception import ExceptionTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.none import NoneTransformer
from poop.transformers.object import ObjectTransformer
from poop.transformers.range import RangeTransformer
from poop.transformers.return_ import ReturnTransformer
from poop.transformers.set import SetTransformer
from poop.transformers.slice import SliceTransformer
from poop.transformers.string import StrTransformer
from poop.transformers.try_ import NAMESPACE as _try_namespace
from poop.transformers.tuple import TupleTransformer
from poop.transformers.unpack import UnpackTransformer
from poop.transformers.varargs import VarargsTransformer
from poop.transformers.with_ import NAMESPACE as _with_namespace
from poop.transformers.zip import ZipTransformer
from poop.types._cloak import cloak_callable

# Declaration order is load-bearing: every transformer runs on the tree
# the previous ones already rewrote (e.g. SliceTransformer relies on
# NoneTransformer having run). This single list drives both the pipeline
# order and the binding merge below, so a new transformer can never be
# wired into one and forgotten in the other.
_TRANSFORMER_CLASSES: _list[type[BaseTransformer]] = [
    BooleanTransformer,
    NoneTransformer,
    EllipsisTransformer,
    ComplexTransformer,
    BytesTransformer,
    ByteArrayTransformer,
    MemoryViewTransformer,
    IntTransformer,
    FloatTransformer,
    StrTransformer,
    EnumerateTransformer,
    ZipTransformer,
    RangeTransformer,
    ListTransformer,
    TupleTransformer,
    DictTransformer,
    SetTransformer,
    FrozenSetTransformer,
    ExceptionTransformer,
    ClassTransformer,
    ObjectTransformer,
    ReturnTransformer,
    BlockTransformer,
    VarargsTransformer,
    UnpackTransformer,
    SliceTransformer,
]

DEFAULT_TRANSFORMERS: _list[Transformer] = [cls() for cls in _TRANSFORMER_CLASSES]

# Bindings sourced from class-based transformers (PascalCase types
# rewritten into POOP equivalents at parse time) and from
# namespace-only modules (lowercase stdlib mirrors injected with no
# AST rewrite). The build below walks both kinds in declaration
# order and refuses duplicate keys so a new transformer can't
# silently overwrite a binding from an earlier one.
# One binding shared by four literal forms rather than declared on whichever
# transformer happens to run first: `[*x]`, `(*x,)`, `{*x}` and `{**x}` all
# resolve their spread through it, and `_merge_bindings` refuses duplicates, so
# it could not live in more than one `BINDINGS` anyway.
_spread_namespace: _dict[str, _object] = {"_poop_spread": _spread}

_BINDING_SOURCES: _list[_dict[str, _object]] = [
    *(cls.BINDINGS for cls in _TRANSFORMER_CLASSES),
    _try_namespace,
    _with_namespace,
    _spread_namespace,
]


# Helper-name suffixes that say how a binding is reached, not what it is:
# `_poop_dict_from_pairs` and `_poop_dict_merge` are both `dict`.
_HELPER_SUFFIXES = ("_from_kwargs", "_from_pairs", "_from", "_literal", "_merge")


def _spelling(key: str) -> str:
    """The POOP-visible name behind a mangled `_poop_*` binding key.

    Derived rather than tabulated: a table is a second list to keep in step
    with `BINDINGS`, and the whole point of this module's build is that a new
    transformer cannot be wired into one place and forgotten in another.
    `iskeyword` restores the trailing underscore POOP already spells its
    keyword substitutes with (`raise_`), so `_poop_raise` reads as `raise_`.
    """
    stem = key.removeprefix("_poop_")
    for suffix in _HELPER_SUFFIXES:
        stem = stem.removesuffix(suffix)
    return f"{stem}_" if _iskeyword(stem) else stem


def _merge_bindings(sources: _list[_dict[str, _object]]) -> _dict[str, _object]:
    """Fold binding sources into one namespace, refusing duplicate keys.

    A later source silently overwriting an earlier binding is the failure this
    guards: it surfaces the collision at import time instead of letting a new
    transformer shadow an existing name.

    Every function binding is also cloaked on the way through. The key stays
    mangled — `no_poop_prefix` reserves it — but CPython builds a wrong-arity
    message from the callee's `__qualname__`, so `range(1, 2, 3, 4)` blamed
    `_poop_range()`: the interpreter naming a spelling it then refuses if the
    reader types it back. The factory-built collection helpers were worse,
    answering `make_iterable_from.<locals>._from()`. Class bindings need
    nothing here; `cloak` already covers them at their definition.
    """
    namespace: _dict[str, _object] = {}
    for src in sources:
        dup = namespace.keys() & src.keys()
        if dup:
            raise RuntimeError(
                f"poop.transformers: duplicate bindings across sources: {sorted(dup)}"
            )
        namespace.update(src)
    for key, value in namespace.items():
        if isinstance(value, _FunctionType):
            cloak_callable(value, _spelling(key))
    return namespace


DEFAULT_NAMESPACE: _dict[str, _object] = _merge_bindings(_BINDING_SOURCES)

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
