from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)

from poop.transformers.array import NAMESPACE as _array_namespace
from poop.transformers.base import Transformer
from poop.transformers.binascii import NAMESPACE as _binascii_namespace
from poop.transformers.bisect import NAMESPACE as _bisect_namespace
from poop.transformers.block import BlockTransformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.byte_array import ByteArrayTransformer
from poop.transformers.bytes import BytesTransformer
from poop.transformers.bz2 import NAMESPACE as _bz2_namespace
from poop.transformers.calendar import NAMESPACE as _calendar_namespace
from poop.transformers.class_ import ClassTransformer
from poop.transformers.codecs import NAMESPACE as _codecs_namespace
from poop.transformers.complex import ComplexTransformer
from poop.transformers.compression import NAMESPACE as _compression_namespace
from poop.transformers.copy import NAMESPACE as _copy_namespace
from poop.transformers.datetime import NAMESPACE as _datetime_namespace
from poop.transformers.decimal import NAMESPACE as _decimal_namespace
from poop.transformers.dict import DictTransformer
from poop.transformers.difflib import NAMESPACE as _difflib_namespace
from poop.transformers.enum import NAMESPACE as _enum_namespace
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.errno import NAMESPACE as _errno_namespace
from poop.transformers.filecmp import NAMESPACE as _filecmp_namespace
from poop.transformers.float import FloatTransformer
from poop.transformers.fnmatch import NAMESPACE as _fnmatch_namespace
from poop.transformers.fractions import NAMESPACE as _fractions_namespace
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.getpass import NAMESPACE as _getpass_namespace
from poop.transformers.glob import NAMESPACE as _glob_namespace
from poop.transformers.graphlib import NAMESPACE as _graphlib_namespace
from poop.transformers.gzip import NAMESPACE as _gzip_namespace
from poop.transformers.hashlib import NAMESPACE as _hashlib_namespace
from poop.transformers.heapq import NAMESPACE as _heapq_namespace
from poop.transformers.hmac import NAMESPACE as _hmac_namespace
from poop.transformers.int import IntTransformer
from poop.transformers.json import NAMESPACE as _json_namespace
from poop.transformers.list import ListTransformer
from poop.transformers.locale import NAMESPACE as _locale_namespace
from poop.transformers.lzma import NAMESPACE as _lzma_namespace
from poop.transformers.math import NAMESPACE as _math_namespace
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.mimetypes import NAMESPACE as _mimetypes_namespace
from poop.transformers.none import NoneTransformer
from poop.transformers.path import NAMESPACE as _path_namespace
from poop.transformers.pickle import NAMESPACE as _pickle_namespace
from poop.transformers.pprint import NAMESPACE as _pprint_namespace
from poop.transformers.raise_ import RaiseTransformer
from poop.transformers.random import NAMESPACE as _random_namespace
from poop.transformers.range import RangeTransformer
from poop.transformers.re import NAMESPACE as _re_namespace
from poop.transformers.secrets import NAMESPACE as _secrets_namespace
from poop.transformers.set import SetTransformer
from poop.transformers.shlex import NAMESPACE as _shlex_namespace
from poop.transformers.shutil import NAMESPACE as _shutil_namespace
from poop.transformers.slice import SliceTransformer
from poop.transformers.sqlite3 import NAMESPACE as _sqlite3_namespace
from poop.transformers.statistics import NAMESPACE as _statistics_namespace
from poop.transformers.string import NAMESPACE as _string_namespace
from poop.transformers.string import StrTransformer
from poop.transformers.struct import NAMESPACE as _struct_namespace
from poop.transformers.tarfile import NAMESPACE as _tarfile_namespace
from poop.transformers.tempfile import NAMESPACE as _tempfile_namespace
from poop.transformers.textwrap import NAMESPACE as _textwrap_namespace
from poop.transformers.tomllib import NAMESPACE as _tomllib_namespace
from poop.transformers.try_ import NAMESPACE as _try_namespace
from poop.transformers.tuple import TupleTransformer
from poop.transformers.unicodedata import NAMESPACE as _unicodedata_namespace
from poop.transformers.uuid import NAMESPACE as _uuid_namespace
from poop.transformers.weakref import NAMESPACE as _weakref_namespace
from poop.transformers.webbrowser import NAMESPACE as _webbrowser_namespace
from poop.transformers.with_ import NAMESPACE as _with_namespace
from poop.transformers.zip import ZipTransformer
from poop.transformers.zipfile import NAMESPACE as _zipfile_namespace
from poop.transformers.zlib import NAMESPACE as _zlib_namespace
from poop.transformers.zoneinfo import NAMESPACE as _zoneinfo_namespace

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
    **_fnmatch_namespace,
    **_copy_namespace,
    **_pprint_namespace,
    **_bisect_namespace,
    **_heapq_namespace,
    **_shlex_namespace,
    **_uuid_namespace,
    **_json_namespace,
    **_tomllib_namespace,
    **_hmac_namespace,
    **_graphlib_namespace,
    **_re_namespace,
    **_hashlib_namespace,
    **_datetime_namespace,
    **_decimal_namespace,
    **_sqlite3_namespace,
    **_string_namespace,
    **_difflib_namespace,
    **_textwrap_namespace,
    **_unicodedata_namespace,
    **_zoneinfo_namespace,
    **_calendar_namespace,
    **_array_namespace,
    **_weakref_namespace,
    **_enum_namespace,
    **_fractions_namespace,
    **_statistics_namespace,
    **_struct_namespace,
    **_codecs_namespace,
    **_filecmp_namespace,
    **_tempfile_namespace,
    **_shutil_namespace,
    **_pickle_namespace,
    **_zlib_namespace,
    **_gzip_namespace,
    **_bz2_namespace,
    **_lzma_namespace,
    **_zipfile_namespace,
    **_tarfile_namespace,
    **_compression_namespace,
    **_locale_namespace,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
