import unicodedata as _unicodedata
from typing import ClassVar

from poop.types.boolean import Boolean, to_boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


class Unicodedata:
    """Namespace mirroring Python's `unicodedata` module.

    Access to the Unicode Character Database: normalization,
    character properties, name lookup, and numeric values. No new
    POOP type — every method takes/returns plain `Str`/`Int`/`Float`/
    `Boolean` values.

    `unicodedata.ucd_3_2_0` (the legacy frozen UCD database) is out of
    scope for v1.
    """

    unidata_version: ClassVar[Str] = Str(_unicodedata.unidata_version)

    # Normalization -------------------------------------------------------

    @staticmethod
    def normalize(form: Str, unistr: Str) -> Str:
        return Str(_unicodedata.normalize(form._value, unistr._value))  # ty: ignore[invalid-argument-type]

    @staticmethod
    def is_normalized(form: Str, unistr: Str) -> Boolean:
        ok = _unicodedata.is_normalized(form._value, unistr._value)  # ty: ignore[invalid-argument-type]
        return to_boolean(ok)

    # Character properties -----------------------------------------------

    @staticmethod
    def category(chr: Str) -> Str:
        return Str(_unicodedata.category(chr._value))

    @staticmethod
    def bidirectional(chr: Str) -> Str:
        return Str(_unicodedata.bidirectional(chr._value))

    @staticmethod
    def combining(chr: Str) -> Int:
        return Int(_unicodedata.combining(chr._value))

    @staticmethod
    def east_asian_width(chr: Str) -> Str:
        return Str(_unicodedata.east_asian_width(chr._value))

    @staticmethod
    def mirrored(chr: Str) -> Int:
        return Int(_unicodedata.mirrored(chr._value))

    @staticmethod
    def decomposition(chr: Str) -> Str:
        return Str(_unicodedata.decomposition(chr._value))

    # Name lookup ---------------------------------------------------------

    @staticmethod
    def name(chr: Str, default: Str | None = None) -> Str:
        if default is None:
            return Str(_unicodedata.name(chr._value))
        return Str(_unicodedata.name(chr._value, default._value))

    @staticmethod
    def lookup(name: Str) -> Str:
        return Str(_unicodedata.lookup(name._value))

    # Numeric values ------------------------------------------------------

    @staticmethod
    def decimal(chr: Str, default: Int | None = None) -> Int:
        if default is None:
            return Int(_unicodedata.decimal(chr._value))
        return Int(_unicodedata.decimal(chr._value, default._value))

    @staticmethod
    def digit(chr: Str, default: Int | None = None) -> Int:
        if default is None:
            return Int(_unicodedata.digit(chr._value))
        return Int(_unicodedata.digit(chr._value, default._value))

    @staticmethod
    def numeric(chr: Str, default: Float | None = None) -> Float:
        if default is None:
            return Float(_unicodedata.numeric(chr._value))
        return Float(_unicodedata.numeric(chr._value, default._value))
