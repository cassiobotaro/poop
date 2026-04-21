from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)

from poop.transformers.base import Transformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.none import NoneTransformer
from poop.transformers.range import RangeTransformer
from poop.transformers.string import StrTransformer
from poop.transformers.tuple import TupleTransformer

DEFAULT_TRANSFORMERS: _list[Transformer] = [
    BooleanTransformer(),
    NoneTransformer(),
    IntTransformer(),
    FloatTransformer(),
    StrTransformer(),
    RangeTransformer(),
    ListTransformer(),
    TupleTransformer(),
]
DEFAULT_NAMESPACE: dict[str, object] = {
    **BooleanTransformer.BINDINGS,
    **NoneTransformer.BINDINGS,
    **IntTransformer.BINDINGS,
    **FloatTransformer.BINDINGS,
    **StrTransformer.BINDINGS,
    **RangeTransformer.BINDINGS,
    **ListTransformer.BINDINGS,
    **TupleTransformer.BINDINGS,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
