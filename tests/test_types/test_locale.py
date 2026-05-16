import pytest

from poop.interpreter import Interpreter
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.locale import Locale
from poop.types.none import NoneClass
from poop.types.string import Str
from poop.types.tuple import Tuple


@pytest.fixture(autouse=True)
def _restore_locale() -> object:
    """`setlocale` is process-global; reset to C between tests."""
    import locale as _stdlib_locale

    saved = _stdlib_locale.setlocale(_stdlib_locale.LC_ALL)
    yield
    _stdlib_locale.setlocale(_stdlib_locale.LC_ALL, saved)


# --- Categories / Error ---


def test_categories_are_ints() -> None:
    assert isinstance(Locale.LC_ALL, Int)
    assert isinstance(Locale.LC_CTYPE, Int)
    assert isinstance(Locale.LC_COLLATE, Int)
    assert isinstance(Locale.LC_TIME, Int)
    assert isinstance(Locale.LC_MONETARY, Int)
    assert isinstance(Locale.LC_NUMERIC, Int)
    assert isinstance(Locale.LC_MESSAGES, Int)


def test_char_max_is_int() -> None:
    assert isinstance(Locale.CHAR_MAX, Int)


def test_error_class_exposed() -> None:
    assert issubclass(Locale.Error, Exception)


def test_setlocale_invalid_raises() -> None:
    with pytest.raises(Locale.Error):
        Locale.setlocale(Locale.LC_ALL, Str("nonexistent.locale.xyz"))


# --- Get / set ---


def test_getlocale_default_category() -> None:
    result = Locale.getlocale()
    assert isinstance(result, Tuple)


def test_getlocale_with_explicit_category() -> None:
    result = Locale.getlocale(Locale.LC_NUMERIC)
    assert isinstance(result, Tuple)


def test_setlocale_to_c_returns_str() -> None:
    result = Locale.setlocale(Locale.LC_ALL, Str("C"))
    assert isinstance(result, Str)


def test_setlocale_query_only() -> None:
    # No `locale` argument queries the current setting.
    result = Locale.setlocale(Locale.LC_ALL)
    assert isinstance(result, Str)


def test_setlocale_with_none_queries() -> None:
    from poop.types.none import none

    result = Locale.setlocale(Locale.LC_ALL, none)
    assert isinstance(result, Str)


def test_getpreferredencoding_returns_str() -> None:
    result = Locale.getpreferredencoding()
    assert isinstance(result, Str)
    assert len(result._value) > 0


def test_getpreferredencoding_no_setlocale() -> None:
    from poop.types.boolean import false

    result = Locale.getpreferredencoding(do_setlocale=false)
    assert isinstance(result, Str)


def test_getdefaultlocale_returns_tuple() -> None:
    result = Locale.getdefaultlocale()
    assert isinstance(result, Tuple)
    # First element is either a Str or none.
    first = result.at(Int(0))
    assert isinstance(first, Str | NoneClass)


# --- Formatting ---


def test_localeconv_returns_dict() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    conv = Locale.localeconv()
    assert isinstance(conv, Dict)
    # Standard keys present in every locale.
    assert conv.includes(Str("decimal_point"))
    assert conv.includes(Str("thousands_sep"))


def test_format_string_decimal() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    result = Locale.format_string(Str("%d"), Int(1234))
    assert result == Str("1234")


def test_format_string_with_grouping() -> None:
    from poop.types.boolean import true

    Locale.setlocale(Locale.LC_ALL, Str("C"))
    result = Locale.format_string(Str("%d"), Int(1234), grouping=true)
    assert isinstance(result, Str)


def test_str_formats_float() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    result = Locale.str(Float(1.25))
    assert result == Str("1.25")


def test_atof_parses_decimal() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    result = Locale.atof(Str("1.5"))
    assert result == Float(1.5)


def test_atoi_parses_integer() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    result = Locale.atoi(Str("42"))
    assert result == Int(42)


def test_delocalize_strips_grouping() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    # In the C locale, delocalize is essentially a no-op.
    result = Locale.delocalize(Str("1234"))
    assert isinstance(result, Str)


def test_normalize_returns_str() -> None:
    result = Locale.normalize(Str("en_US"))
    assert isinstance(result, Str)


def test_currency_in_c_locale_raises() -> None:
    # The C locale has no monetary symbol; CPython raises ValueError.
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    with pytest.raises(ValueError):
        Locale.currency(Float(1234.56))


def test_currency_keyword_args_accepted() -> None:
    from poop.types.boolean import false, true

    Locale.setlocale(Locale.LC_ALL, Str("C"))
    with pytest.raises(ValueError):
        Locale.currency(
            Float(1.0),
            symbol=false,
            grouping=true,
            international=false,
        )


# --- Collation ---


def test_strcoll_returns_int() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    assert Locale.strcoll(Str("a"), Str("b"))._value < 0
    assert Locale.strcoll(Str("z"), Str("a"))._value > 0
    assert Locale.strcoll(Str("a"), Str("a")) == Int(0)


def test_strxfrm_returns_str() -> None:
    Locale.setlocale(Locale.LC_ALL, Str("C"))
    result = Locale.strxfrm(Str("alpha"))
    assert isinstance(result, Str)


# --- Interpreter integration ---


def test_locale_getpreferredencoding_via_interpreter() -> None:
    Interpreter().run_source("locale.getpreferredencoding().print()")


def test_locale_setlocale_via_interpreter() -> None:
    Interpreter().run_source('locale.setlocale(locale.LC_ALL, "C").print()')


def test_locale_categories_via_interpreter() -> None:
    Interpreter().run_source("locale.LC_ALL.print()")
