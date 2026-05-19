from __future__ import annotations

import codecs as _codecs
from typing import Any, ClassVar

from poop.types._unwrap import _opt_str
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import NoneClass
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_arg(obj: Bytes | Str) -> Any:
    if isinstance(obj, Bytes | Str):
        return obj._value
    raise TypeError(f"codecs expects Bytes or Str, got {type(obj).__name__}")


def _wrap_result(value: Any) -> Bytes | Str:
    if isinstance(value, bytes | bytearray):
        return Bytes(bytes(value))
    if isinstance(value, str):
        return Str(value)
    raise TypeError(f"codec returned unsupported type: {type(value).__name__}")


def _opt_errors(errors: Str | NoneClass | None) -> str:
    return _opt_str(errors, "strict")


class CodecInfo:
    """Wraps Python's `codecs.CodecInfo` namedtuple.

    Exposes the codec name plus `.encode` / `.decode` shortcuts (each
    returns `(result, length_consumed)` as a `Tuple`, matching CPython).
    Incremental codec construction is out of scope — those entry points
    would expose raw CPython encoder/decoder classes.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: _codecs.CodecInfo) -> None:
        self._impl = impl

    @property
    def name(self) -> Str:
        return Str(self._impl.name)

    def encode(self, obj: Bytes | Str, errors: Str | None = None) -> Tuple:
        result, length = self._impl.encode(_unwrap_arg(obj), _opt_errors(errors))
        return Tuple(_wrap_result(result), Int(length))

    def decode(self, obj: Bytes | Str, errors: Str | None = None) -> Tuple:
        result, length = self._impl.decode(_unwrap_arg(obj), _opt_errors(errors))
        return Tuple(_wrap_result(result), Int(length))

    def __str__(self) -> str:
        return f"<CodecInfo {self._impl.name}>"

    __repr__ = __str__


class Codecs:
    """Namespace mirroring Python's `codecs` module.

    Direct encode/decode helpers cover the codec-as-function surface;
    BOM constants expose the standard byte-order marks; `lookup`
    returns a `CodecInfo` wrapper for callers that need codec metadata
    or the incremental encoder/decoder classes.

    Incremental encoder/decoder construction, `StreamReader` /
    `StreamWriter`, and the `register` / `register_error` extension
    hooks are out of scope for v1.

    `codecs.LookupError` is the Python `LookupError` raised when the
    requested codec name doesn't resolve.
    """

    # BOM constants ------------------------------------------------------

    BOM_UTF8: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF8)
    BOM_UTF16: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF16)
    BOM_UTF16_LE: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF16_LE)
    BOM_UTF16_BE: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF16_BE)
    BOM_UTF32: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF32)
    BOM_UTF32_LE: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF32_LE)
    BOM_UTF32_BE: ClassVar[Bytes] = Bytes(_codecs.BOM_UTF32_BE)
    BOM: ClassVar[Bytes] = Bytes(_codecs.BOM)
    BOM_LE: ClassVar[Bytes] = Bytes(_codecs.BOM_LE)
    BOM_BE: ClassVar[Bytes] = Bytes(_codecs.BOM_BE)

    CodecInfo: ClassVar[type[CodecInfo]] = CodecInfo

    # Codec lookup -------------------------------------------------------

    @staticmethod
    def encode(
        obj: Bytes | Str,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Bytes | Str:
        enc = _opt_str(encoding, "utf-8")
        return _wrap_result(_codecs.encode(_unwrap_arg(obj), enc, _opt_errors(errors)))

    @staticmethod
    def decode(
        obj: Bytes | Str,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Bytes | Str:
        enc = _opt_str(encoding, "utf-8")
        return _wrap_result(_codecs.decode(_unwrap_arg(obj), enc, _opt_errors(errors)))

    @staticmethod
    def lookup(encoding: Str) -> CodecInfo:
        return CodecInfo(_codecs.lookup(encoding._value))
