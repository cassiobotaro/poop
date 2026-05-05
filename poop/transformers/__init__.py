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
from poop.transformers.dict import DictTransformer
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.none import NoneTransformer
from poop.transformers.raise_ import RaiseTransformer
from poop.transformers.range import RangeTransformer
from poop.transformers.set import SetTransformer
from poop.transformers.slice import SliceTransformer
from poop.transformers.string import StrTransformer
from poop.transformers.try_ import TryTransformer
from poop.transformers.tuple import TupleTransformer
from poop.transformers.with_ import WithTransformer

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
    RangeTransformer(),
    ListTransformer(),
    TupleTransformer(),
    DictTransformer(),
    SetTransformer(),
    FrozenSetTransformer(),
    RaiseTransformer(),
    ClassTransformer(),
    BlockTransformer(),
    SliceTransformer(),
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
    **EnumerateTransformer.BINDINGS,
    **RangeTransformer.BINDINGS,
    **ListTransformer.BINDINGS,
    **TupleTransformer.BINDINGS,
    **DictTransformer.BINDINGS,
    **SetTransformer.BINDINGS,
    **FrozenSetTransformer.BINDINGS,
    **RaiseTransformer.BINDINGS,
    **ClassTransformer.BINDINGS,
    **TryTransformer.BINDINGS,
    **WithTransformer.BINDINGS,
    **SliceTransformer.BINDINGS,
    **BlockTransformer.BINDINGS,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
