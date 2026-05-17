import binascii as _binascii
from typing import TYPE_CHECKING, ClassVar

from poop.types._unwrap import _unwrap
from poop.types.bytes import Bytes
from poop.types.int import Int

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class Binascii:
    """Namespace mirroring Python's `binascii` module.

    Conversions between binary data and ASCII-encoded representations
    (hex / base64 / quoted-printable / uu) plus CRC checksums.

    The two exception classes — `binascii.Error` and
    `binascii.Incomplete` — are exposed as raw Python types on the
    namespace so user code can pass them to `Try.except_(...)`.
    Exception classes are the documented exception to the type-
    discipline rule: `Try` already takes a Python exception type for
    its handler, so exposing these mirrors the existing convention.

    `b2a_hqx`/`a2b_hqx` (Mac BinHex 4) are out of scope — Python
    removed them in 3.13.
    """

    # Exception classes (Python types — see docstring).
    Error: ClassVar[type[Exception]] = _binascii.Error
    Incomplete: ClassVar[type[Exception]] = _binascii.Incomplete

    # Hex --------------------------------------------------------------

    @staticmethod
    def b2a_hex(
        data: Bytes,
        sep: Bytes | NoneClass | None = None,
        bytes_per_sep: Int | None = None,
    ) -> Bytes:
        from poop.types.none import NoneClass as _NoneClass

        sep_value = None if sep is None or isinstance(sep, _NoneClass) else sep._value
        n = _unwrap(bytes_per_sep, 1)
        if sep_value is None:
            return Bytes(_binascii.b2a_hex(data._value))
        return Bytes(_binascii.b2a_hex(data._value, sep_value, n))

    @staticmethod
    def hexlify(
        data: Bytes,
        sep: Bytes | NoneClass | None = None,
        bytes_per_sep: Int | None = None,
    ) -> Bytes:
        return Binascii.b2a_hex(data, sep, bytes_per_sep)

    @staticmethod
    def a2b_hex(hexstr: Bytes) -> Bytes:
        return Bytes(_binascii.a2b_hex(hexstr._value))

    @staticmethod
    def unhexlify(hexstr: Bytes) -> Bytes:
        return Bytes(_binascii.unhexlify(hexstr._value))

    # Base64 / qp / uu (one-shot lower-level than `base64`) -----------

    @staticmethod
    def b2a_base64(data: Bytes) -> Bytes:
        return Bytes(_binascii.b2a_base64(data._value))

    @staticmethod
    def a2b_base64(data: Bytes) -> Bytes:
        return Bytes(_binascii.a2b_base64(data._value))

    @staticmethod
    def b2a_qp(data: Bytes) -> Bytes:
        return Bytes(_binascii.b2a_qp(data._value))

    @staticmethod
    def a2b_qp(data: Bytes) -> Bytes:
        return Bytes(_binascii.a2b_qp(data._value))

    @staticmethod
    def b2a_uu(data: Bytes) -> Bytes:
        return Bytes(_binascii.b2a_uu(data._value))

    @staticmethod
    def a2b_uu(data: Bytes) -> Bytes:
        return Bytes(_binascii.a2b_uu(data._value))

    # CRC --------------------------------------------------------------

    @staticmethod
    def crc_hqx(data: Bytes, value: Int) -> Int:
        return Int(_binascii.crc_hqx(data._value, value._value))

    @staticmethod
    def crc32(data: Bytes, value: Int | None = None) -> Int:
        return Int(_binascii.crc32(data._value, _unwrap(value, 0)))
