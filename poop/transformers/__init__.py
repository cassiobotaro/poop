from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)

from poop.transformers.base import Transformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.byte_array import ByteArrayTransformer
from poop.transformers.bytes import BytesTransformer
from poop.transformers.complex import ComplexTransformer
from poop.transformers.dict import DictTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.none import NoneTransformer
from poop.transformers.raise_ import RaiseTransformer
from poop.transformers.range import RangeTransformer
from poop.transformers.set import SetTransformer
from poop.transformers.string import StrTransformer
from poop.transformers.tuple import TupleTransformer

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
    RangeTransformer(),
    ListTransformer(),
    TupleTransformer(),
    DictTransformer(),
    SetTransformer(),
    FrozenSetTransformer(),
    RaiseTransformer(),
]
DEFAULT_NAMESPACE: _dict[str, object] = {
    **BooleanTransformer.BINDINGS,
    **NoneTransformer.BINDINGS,
    **ComplexTransformer.BINDINGS,
    **BytesTransformer.BINDINGS,
    **ByteArrayTransformer.BINDINGS,
    **MemoryViewTransformer.BINDINGS,
    **IntTransformer.BINDINGS,
    **FloatTransformer.BINDINGS,
    **StrTransformer.BINDINGS,
    **RangeTransformer.BINDINGS,
    **ListTransformer.BINDINGS,
    **TupleTransformer.BINDINGS,
    **DictTransformer.BINDINGS,
    **SetTransformer.BINDINGS,
    **FrozenSetTransformer.BINDINGS,
    **RaiseTransformer.BINDINGS,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
