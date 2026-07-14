from builtins import (
    dict as _dict,  # preserve builtin before poop.transformers.dict shadows it
)
from builtins import (
    list as _list,  # preserve builtin before poop.transformers.list shadows it
)

from poop.transformers.array import NAMESPACE as _array_namespace
from poop.transformers.asyncio import NAMESPACE as _asyncio_namespace
from poop.transformers.atexit import NAMESPACE as _atexit_namespace
from poop.transformers.base import Transformer
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
from poop.transformers.concurrent import NAMESPACE as _concurrent_namespace
from poop.transformers.configparser import NAMESPACE as _configparser_namespace
from poop.transformers.csv import NAMESPACE as _csv_namespace
from poop.transformers.datetime import NAMESPACE as _datetime_namespace
from poop.transformers.decimal import NAMESPACE as _decimal_namespace
from poop.transformers.dict import DictTransformer
from poop.transformers.difflib import NAMESPACE as _difflib_namespace
from poop.transformers.email import NAMESPACE as _email_namespace
from poop.transformers.enum import NAMESPACE as _enum_namespace
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.filecmp import NAMESPACE as _filecmp_namespace
from poop.transformers.float import FloatTransformer
from poop.transformers.fractions import NAMESPACE as _fractions_namespace
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.gc import NAMESPACE as _gc_namespace
from poop.transformers.graphlib import NAMESPACE as _graphlib_namespace
from poop.transformers.grp import NAMESPACE as _grp_namespace
from poop.transformers.gzip import NAMESPACE as _gzip_namespace
from poop.transformers.hashlib import NAMESPACE as _hashlib_namespace
from poop.transformers.hmac import NAMESPACE as _hmac_namespace
from poop.transformers.html import NAMESPACE as _html_namespace
from poop.transformers.http import NAMESPACE as _http_namespace
from poop.transformers.int import IntTransformer
from poop.transformers.io import NAMESPACE as _io_namespace
from poop.transformers.ipaddress import NAMESPACE as _ipaddress_namespace
from poop.transformers.json import NAMESPACE as _json_namespace
from poop.transformers.list import ListTransformer
from poop.transformers.locale import NAMESPACE as _locale_namespace
from poop.transformers.logging import NAMESPACE as _logging_namespace
from poop.transformers.lzma import NAMESPACE as _lzma_namespace
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.multiprocessing import NAMESPACE as _multiprocessing_namespace
from poop.transformers.none import NoneTransformer
from poop.transformers.os import NAMESPACE as _os_namespace
from poop.transformers.path import NAMESPACE as _path_namespace
from poop.transformers.pickle import NAMESPACE as _pickle_namespace
from poop.transformers.platform import NAMESPACE as _platform_namespace
from poop.transformers.profile import NAMESPACE as _profile_namespace
from poop.transformers.pwd import NAMESPACE as _pwd_namespace
from poop.transformers.queue import NAMESPACE as _queue_namespace
from poop.transformers.raise_ import RaiseTransformer
from poop.transformers.random import NAMESPACE as _random_namespace
from poop.transformers.range import RangeTransformer
from poop.transformers.re import NAMESPACE as _re_namespace
from poop.transformers.resource import NAMESPACE as _resource_namespace
from poop.transformers.return_ import ReturnTransformer
from poop.transformers.set import SetTransformer
from poop.transformers.shutil import NAMESPACE as _shutil_namespace
from poop.transformers.signal import NAMESPACE as _signal_namespace
from poop.transformers.slice import SliceTransformer
from poop.transformers.smtplib import NAMESPACE as _smtplib_namespace
from poop.transformers.socket import NAMESPACE as _socket_namespace
from poop.transformers.sqlite3 import NAMESPACE as _sqlite3_namespace
from poop.transformers.ssl import NAMESPACE as _ssl_namespace
from poop.transformers.statistics import NAMESPACE as _statistics_namespace
from poop.transformers.string import NAMESPACE as _string_namespace
from poop.transformers.string import StrTransformer
from poop.transformers.struct import NAMESPACE as _struct_namespace
from poop.transformers.subprocess import NAMESPACE as _subprocess_namespace
from poop.transformers.sys import NAMESPACE as _sys_namespace
from poop.transformers.tarfile import NAMESPACE as _tarfile_namespace
from poop.transformers.tempfile import NAMESPACE as _tempfile_namespace
from poop.transformers.textwrap import NAMESPACE as _textwrap_namespace
from poop.transformers.threading import NAMESPACE as _threading_namespace
from poop.transformers.time import NAMESPACE as _time_namespace
from poop.transformers.timeit import NAMESPACE as _timeit_namespace
from poop.transformers.tomllib import NAMESPACE as _tomllib_namespace
from poop.transformers.try_ import NAMESPACE as _try_namespace
from poop.transformers.tuple import TupleTransformer
from poop.transformers.unicodedata import NAMESPACE as _unicodedata_namespace
from poop.transformers.unittest import NAMESPACE as _unittest_namespace
from poop.transformers.unpack import UnpackTransformer
from poop.transformers.urllib import NAMESPACE as _urllib_namespace
from poop.transformers.uuid import NAMESPACE as _uuid_namespace
from poop.transformers.varargs import VarargsTransformer
from poop.transformers.weakref import NAMESPACE as _weakref_namespace
from poop.transformers.with_ import NAMESPACE as _with_namespace
from poop.transformers.xml import NAMESPACE as _xml_namespace
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
    _random_namespace,
    _uuid_namespace,
    _json_namespace,
    _tomllib_namespace,
    _hmac_namespace,
    _graphlib_namespace,
    _re_namespace,
    _hashlib_namespace,
    _datetime_namespace,
    _decimal_namespace,
    _sqlite3_namespace,
    _string_namespace,
    _difflib_namespace,
    _textwrap_namespace,
    _unicodedata_namespace,
    _zoneinfo_namespace,
    _calendar_namespace,
    _array_namespace,
    _weakref_namespace,
    _enum_namespace,
    _fractions_namespace,
    _statistics_namespace,
    _struct_namespace,
    _codecs_namespace,
    _filecmp_namespace,
    _tempfile_namespace,
    _shutil_namespace,
    _pickle_namespace,
    _zlib_namespace,
    _gzip_namespace,
    _bz2_namespace,
    _lzma_namespace,
    _zipfile_namespace,
    _tarfile_namespace,
    _compression_namespace,
    _locale_namespace,
    _ipaddress_namespace,
    _urllib_namespace,
    _http_namespace,
    _smtplib_namespace,
    _csv_namespace,
    _configparser_namespace,
    _pwd_namespace,
    _grp_namespace,
    _resource_namespace,
    _sys_namespace,
    _atexit_namespace,
    _gc_namespace,
    _email_namespace,
    _html_namespace,
    _xml_namespace,
    _unittest_namespace,
    _profile_namespace,
    _timeit_namespace,
    _signal_namespace,
    _socket_namespace,
    _ssl_namespace,
    _asyncio_namespace,
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
