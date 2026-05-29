from __future__ import annotations

import locale as _locale
from typing import Any, ClassVar

from poop.types._unwrap import _b
from poop.types.boolean import Boolean, false
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.string import Str
from poop.types.tuple import Tuple


def _wrap_locale_pair(pair: tuple[Any, Any]) -> Tuple:
    lang, enc = pair
    return Tuple(
        none if lang is None else Str(lang),
        none if enc is None else Str(enc),
    )


def _wrap_localeconv_value(value: Any) -> Any:
    if isinstance(value, bool):
        from poop.types.boolean import to_boolean

        return to_boolean(value)
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, str):
        return Str(value)
    if isinstance(value, list):
        return List(*(_wrap_localeconv_value(v) for v in value))
    return value


class Locale:
    """Namespace mirroring Python's `locale` module — locale-aware
    formatting (currency, decimal separators, collation, month names).

    `setlocale` / `getlocale` accept the standard `LC_*` category
    constants; `localeconv` returns the full convention map as a POOP
    `Dict`. `format_string` / `currency` / `str` cover formatting;
    `atof` / `atoi` / `delocalize` parse locale-specific number
    strings; `strcoll` / `strxfrm` cover collation.
    """

    # Categories.
    LC_ALL: ClassVar[Int] = Int(_locale.LC_ALL)
    LC_CTYPE: ClassVar[Int] = Int(_locale.LC_CTYPE)
    LC_COLLATE: ClassVar[Int] = Int(_locale.LC_COLLATE)
    LC_TIME: ClassVar[Int] = Int(_locale.LC_TIME)
    LC_MONETARY: ClassVar[Int] = Int(_locale.LC_MONETARY)
    LC_NUMERIC: ClassVar[Int] = Int(_locale.LC_NUMERIC)

    # LC_MESSAGES is POSIX-only; on Windows it's absent. Expose when
    # available; otherwise fall back to `LC_ALL` so user code reading
    # the attribute doesn't crash on platforms missing it.
    LC_MESSAGES: ClassVar[Int] = Int(getattr(_locale, "LC_MESSAGES", _locale.LC_ALL))

    CHAR_MAX: ClassVar[Int] = Int(_locale.CHAR_MAX)

    Error: ClassVar[type[Exception]] = _locale.Error

    # Get / set ---------------------------------------------------------

    @staticmethod
    def getlocale(category: Int | None = None) -> Tuple:
        cat = _locale.LC_CTYPE if category is None else category._value
        return _wrap_locale_pair(_locale.getlocale(cat))

    @staticmethod
    def setlocale(category: Int, locale: Str | NoneClass | None = None) -> Str:
        if locale is None or isinstance(locale, NoneClass):
            return Str(_locale.setlocale(category._value))
        return Str(_locale.setlocale(category._value, locale._value))

    @staticmethod
    def getdefaultlocale() -> Tuple:
        # `getdefaultlocale` is deprecated since 3.11 but still in the
        # docs; we expose it so callers writing portable code can keep
        # using the old idiom while planning their migration.
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            return _wrap_locale_pair(_locale.getdefaultlocale())

    @staticmethod
    def getpreferredencoding(do_setlocale: Boolean | None = None) -> Str:
        return Str(_locale.getpreferredencoding(_b(do_setlocale, True)))

    # Formatting --------------------------------------------------------

    @staticmethod
    def localeconv() -> Dict:
        raw = _locale.localeconv()
        result = Dict()
        for key, value in raw.items():
            result.at_put(Str(key), _wrap_localeconv_value(value))
        return result

    @staticmethod
    def format_string(
        f: Str,
        val: Int | Float,
        grouping: Boolean = false,
        monetary: Boolean = false,
    ) -> Str:
        return Str(
            _locale.format_string(
                f._value,
                val._value,
                bool(grouping),
                bool(monetary),
            )
        )

    @staticmethod
    def currency(
        val: Int | Float,
        symbol: Boolean | None = None,
        grouping: Boolean | None = None,
        international: Boolean | None = None,
    ) -> Str:
        return Str(
            _locale.currency(
                val._value,
                symbol=_b(symbol, True),
                grouping=_b(grouping, False),
                international=_b(international, False),
            )
        )

    @staticmethod
    def str(val: Float) -> Str:
        return Str(_locale.str(val._value))

    @staticmethod
    def atof(string: Str, func: Any = None) -> Float:
        # `func` (CPython callable to convert the parsed Python number) is
        # ignored — POOP doesn't surface a Float-vs-Decimal sentinel here;
        # the result is always a POOP `Float`. Defer richer support.
        del func
        return Float(_locale.atof(string._value))

    @staticmethod
    def atoi(string: Str) -> Int:
        return Int(_locale.atoi(string._value))

    @staticmethod
    def delocalize(string: Str) -> Str:
        return Str(_locale.delocalize(string._value))

    @staticmethod
    def normalize(localename: Str) -> Str:
        return Str(_locale.normalize(localename._value))

    # Collation ---------------------------------------------------------

    @staticmethod
    def strcoll(os1: Str, os2: Str, /) -> Int:
        return Int(_locale.strcoll(os1._value, os2._value))

    @staticmethod
    def strxfrm(string: Str) -> Str:
        return Str(_locale.strxfrm(string._value))
