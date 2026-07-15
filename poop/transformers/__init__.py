from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)

from poop.transformers.base import Transformer
from poop.transformers.block import BlockTransformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.byte_array import ByteArrayTransformer
from poop.transformers.bytes import BytesTransformer
from poop.transformers.class_ import ClassTransformer
from poop.transformers.complex import ComplexTransformer
from poop.transformers.concurrent import NAMESPACE as _concurrent_namespace
from poop.transformers.dict import DictTransformer
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.io import NAMESPACE as _io_namespace
from poop.transformers.list import ListTransformer
from poop.transformers.logging import NAMESPACE as _logging_namespace
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.multiprocessing import NAMESPACE as _multiprocessing_namespace
from poop.transformers.none import NoneTransformer
from poop.transformers.os import NAMESPACE as _os_namespace
from poop.transformers.path import NAMESPACE as _path_namespace
from poop.transformers.platform import NAMESPACE as _platform_namespace
from poop.transformers.queue import NAMESPACE as _queue_namespace
from poop.transformers.raise_ import RaiseTransformer
from poop.transformers.range import RangeTransformer
from poop.transformers.return_ import ReturnTransformer
from poop.transformers.set import SetTransformer
from poop.transformers.slice import SliceTransformer
from poop.transformers.string import NAMESPACE as _string_namespace
from poop.transformers.string import StrTransformer
from poop.transformers.subprocess import NAMESPACE as _subprocess_namespace
from poop.transformers.threading import NAMESPACE as _threading_namespace
from poop.transformers.time import NAMESPACE as _time_namespace
from poop.transformers.try_ import NAMESPACE as _try_namespace
from poop.transformers.tuple import TupleTransformer
from poop.transformers.unpack import UnpackTransformer
from poop.transformers.varargs import VarargsTransformer
from poop.transformers.with_ import NAMESPACE as _with_namespace
from poop.transformers.zip import ZipTransformer

DEFAULT_TRANSFORMERS: _list[Transformer] = [
    BooleanTransformer(),
    NoneTransformer(),
    ComplexTransformer(),
    BytesTransformer(),
    ByteArrayTransformer(),
    MemoryViewTransformer(),
    IntTransformer(),
    FloatTransformer(),
    StrTransformer(),
    EnumerateTransformer(),
    ZipTransformer(),
    RangeTransformer(),
    ListTransformer(),
    TupleTransformer(),
    DictTransformer(),
    SetTransformer(),
    FrozenSetTransformer(),
    RaiseTransformer(),
    ClassTransformer(),
    ReturnTransformer(),
    BlockTransformer(),
    VarargsTransformer(),
    UnpackTransformer(),
    SliceTransformer(),
]
# Bindings sourced from class-based transformers (PascalCase types
# rewritten into POOP equivalents at parse time) and from
# namespace-only modules (lowercase stdlib mirrors injected with no
# AST rewrite). The build below walks both kinds in declaration
# order and refuses duplicate keys so a new transformer can't
# silently overwrite a binding from an earlier one.
_BINDING_SOURCES: _list[_dict[str, object]] = [
    BooleanTransformer.BINDINGS,
    NoneTransformer.BINDINGS,
    ComplexTransformer.BINDINGS,
    BytesTransformer.BINDINGS,
    ByteArrayTransformer.BINDINGS,
    MemoryViewTransformer.BINDINGS,
    IntTransformer.BINDINGS,
    FloatTransformer.BINDINGS,
    StrTransformer.BINDINGS,
    EnumerateTransformer.BINDINGS,
    ZipTransformer.BINDINGS,
    RangeTransformer.BINDINGS,
    ListTransformer.BINDINGS,
    TupleTransformer.BINDINGS,
    DictTransformer.BINDINGS,
    SetTransformer.BINDINGS,
    FrozenSetTransformer.BINDINGS,
    RaiseTransformer.BINDINGS,
    ClassTransformer.BINDINGS,
    _try_namespace,
    _with_namespace,
    SliceTransformer.BINDINGS,
    BlockTransformer.BINDINGS,
    _path_namespace,
    _string_namespace,
    _os_namespace,
    _io_namespace,
    _time_namespace,
    _logging_namespace,
    _platform_namespace,
    _threading_namespace,
    _multiprocessing_namespace,
    _concurrent_namespace,
    _subprocess_namespace,
    _queue_namespace,
]

DEFAULT_NAMESPACE: _dict[str, object] = {}
for _src in _BINDING_SOURCES:
    _dup = DEFAULT_NAMESPACE.keys() & _src.keys()
    if _dup:
        raise RuntimeError(
            f"poop.transformers: duplicate bindings across sources: {sorted(_dup)}"
        )
    DEFAULT_NAMESPACE.update(_src)

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
