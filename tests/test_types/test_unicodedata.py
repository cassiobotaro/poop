import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str
from poop.types.unicodedata import Unicodedata

# --- Normalization ---


def test_normalize_nfc_combines_marks() -> None:
    # "e" + combining acute → single "é"
    decomposed = Str("é")
    result = Unicodedata.normalize(Str("NFC"), decomposed)
    assert result == Str("é")


def test_normalize_nfd_decomposes() -> None:
    composed = Str("é")
    result = Unicodedata.normalize(Str("NFD"), composed)
    assert result == Str("é")


def test_is_normalized_true_for_normalized_string() -> None:
    assert Unicodedata.is_normalized(Str("NFC"), Str("hello")) is true


def test_is_normalized_false_for_unnormalized_string() -> None:
    decomposed = Str("é")
    assert Unicodedata.is_normalized(Str("NFC"), decomposed) is false


# --- Character properties ---


def test_category_letter() -> None:
    assert Unicodedata.category(Str("A")) == Str("Lu")


def test_category_digit() -> None:
    assert Unicodedata.category(Str("5")) == Str("Nd")


def test_bidirectional_letter() -> None:
    assert Unicodedata.bidirectional(Str("A")) == Str("L")


def test_combining_basic_letter_zero() -> None:
    assert Unicodedata.combining(Str("A")) == Int(0)


def test_combining_acute_accent() -> None:
    result = Unicodedata.combining(Str("́"))
    assert isinstance(result, Int)
    assert result._value > 0


def test_east_asian_width_ascii() -> None:
    assert Unicodedata.east_asian_width(Str("A")) == Str("Na")


def test_mirrored_paren() -> None:
    assert Unicodedata.mirrored(Str("(")) == Int(1)


def test_mirrored_letter() -> None:
    assert Unicodedata.mirrored(Str("A")) == Int(0)


def test_decomposition_returns_str() -> None:
    result = Unicodedata.decomposition(Str("é"))
    assert isinstance(result, Str)
    assert result._value != ""


# --- Name lookup ---


def test_name_letter_a() -> None:
    assert Unicodedata.name(Str("A")) == Str("LATIN CAPITAL LETTER A")


def test_name_default_for_unnamed() -> None:
    # Control characters have no name; default kicks in.
    result = Unicodedata.name(Str("\x00"), default=Str("unknown"))
    assert result == Str("unknown")


def test_name_no_default_raises() -> None:
    with pytest.raises(ValueError):
        Unicodedata.name(Str("\x00"))


def test_lookup_by_name() -> None:
    assert Unicodedata.lookup(Str("LATIN CAPITAL LETTER A")) == Str("A")


def test_lookup_invalid_raises() -> None:
    with pytest.raises(KeyError):
        Unicodedata.lookup(Str("NOT A REAL CHARACTER NAME"))


# --- Numeric values ---


def test_decimal_digit_returns_int() -> None:
    assert Unicodedata.decimal(Str("7")) == Int(7)


def test_decimal_letter_default() -> None:
    assert Unicodedata.decimal(Str("A"), default=Int(-1)) == Int(-1)


def test_digit_returns_int() -> None:
    assert Unicodedata.digit(Str("9")) == Int(9)


def test_numeric_fraction() -> None:
    # "½" U+00BD has numeric value 0.5
    result = Unicodedata.numeric(Str("½"))
    assert isinstance(result, Float)
    assert result == Float(0.5)


def test_numeric_default() -> None:
    result = Unicodedata.numeric(Str("A"), default=Float(-1.0))
    assert result == Float(-1.0)


# --- Version constant ---


def test_unidata_version_is_str() -> None:
    assert isinstance(Unicodedata.unidata_version, Str)
    assert "." in Unicodedata.unidata_version._value


# --- Interpreter integration ---


def test_unicodedata_category_reachable_via_interpreter() -> None:
    Interpreter().run_source('unicodedata.category("A").print()')


def test_unicodedata_name_reachable_via_interpreter() -> None:
    Interpreter().run_source('unicodedata.name("Z").print()')


def test_unicodedata_normalize_reachable_via_interpreter() -> None:
    Interpreter().run_source('unicodedata.normalize("NFC", "abc").print()')
