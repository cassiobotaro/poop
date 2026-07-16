from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)
from builtins import (
    object as _object,  # preserve builtin before poop.transformers.object shadows it
)

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
from poop.transformers.raise_ import RaiseTransformer
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
    RaiseTransformer,
    # After RaiseTransformer: it matches an uppercase Name followed by
    # `.raise_(...)`, which `_poop_ValueError` is not.
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
_BINDING_SOURCES: _list[_dict[str, _object]] = [
    *(cls.BINDINGS for cls in _TRANSFORMER_CLASSES),
    _try_namespace,
    _with_namespace,
]

DEFAULT_NAMESPACE: _dict[str, _object] = {}
for _src in _BINDING_SOURCES:
    _dup = DEFAULT_NAMESPACE.keys() & _src.keys()
    if _dup:
        raise RuntimeError(
            f"poop.transformers: duplicate bindings across sources: {sorted(_dup)}"
        )
    DEFAULT_NAMESPACE.update(_src)

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
