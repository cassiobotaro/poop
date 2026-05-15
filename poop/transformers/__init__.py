from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)

from poop.transformers.base import Transformer
from poop.transformers.binascii import NAMESPACE as _binascii_namespace
from poop.transformers.block import BlockTransformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.byte_array import ByteArrayTransformer
from poop.transformers.bytes import BytesTransformer
from poop.transformers.class_ import ClassTransformer
from poop.transformers.complex import ComplexTransformer
from poop.transformers.dict import DictTransformer
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.errno import NAMESPACE as _errno_namespace
from poop.transformers.float import FloatTransformer
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.getpass import NAMESPACE as _getpass_namespace
from poop.transformers.glob import NAMESPACE as _glob_namespace
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.math import NAMESPACE as _math_namespace
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.mimetypes import NAMESPACE as _mimetypes_namespace
from poop.transformers.none import NoneTransformer
from poop.transformers.path import NAMESPACE as _path_namespace
from poop.transformers.raise_ import RaiseTransformer
from poop.transformers.random import NAMESPACE as _random_namespace
from poop.transformers.range import RangeTransformer
from poop.transformers.secrets import NAMESPACE as _secrets_namespace
from poop.transformers.set import SetTransformer
from poop.transformers.slice import SliceTransformer
from poop.transformers.string import StrTransformer
from poop.transformers.try_ import NAMESPACE as _try_namespace
from poop.transformers.tuple import TupleTransformer
from poop.transformers.webbrowser import NAMESPACE as _webbrowser_namespace
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
    **ZipTransformer.BINDINGS,
    **RangeTransformer.BINDINGS,
    **ListTransformer.BINDINGS,
    **TupleTransformer.BINDINGS,
    **DictTransformer.BINDINGS,
    **SetTransformer.BINDINGS,
    **FrozenSetTransformer.BINDINGS,
    **RaiseTransformer.BINDINGS,
    **ClassTransformer.BINDINGS,
    **_try_namespace,
    **_with_namespace,
    **SliceTransformer.BINDINGS,
    **BlockTransformer.BINDINGS,
    **_path_namespace,
    **_math_namespace,
    **_random_namespace,
    **_errno_namespace,
    **_getpass_namespace,
    **_secrets_namespace,
    **_binascii_namespace,
    **_mimetypes_namespace,
    **_webbrowser_namespace,
    **_glob_namespace,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
