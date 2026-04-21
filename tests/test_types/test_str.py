import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.string import Str


def test_str_wraps_value() -> None:
    assert str(Str("hello")) == "hello"


def test_len() -> None:
    assert Str("hello").len() == Int(5)


def test_len_empty() -> None:
    assert Str("").len() == Int(0)


def test_at_returns_char() -> None:
    assert Str("hello").at(Int(0)) == Str("h")


def test_at_last_char() -> None:
    assert Str("hello").at(Int(4)) == Str("o")


def test_at_out_of_bounds_raises() -> None:
    with pytest.raises(IndexError):
        Str("hello").at(Int(10))


def test_includes_found() -> None:
    assert Str("hello").includes(Str("e")) is true


def test_includes_not_found() -> None:
    assert Str("hello").includes(Str("z")) is false


def test_reversed() -> None:
    assert Str("hello").reversed() == Str("olleh")


def test_reversed_empty() -> None:
    assert Str("").reversed() == Str("")


def test_add_concatenates() -> None:
    assert Str("hello") + Str(" world") == Str("hello world")


def test_eq_same() -> None:
    assert Str("hello") == Str("hello")


def test_eq_different() -> None:
    assert (Str("hello") == Str("world")) is false


def test_ne() -> None:
    assert (Str("hello") != Str("world")) is true


def test_hash_consistent() -> None:
    assert hash(Str("hello")) == hash(Str("hello"))


def test_str_repr_delegates() -> None:
    s = Str("hi")
    assert repr(s) == str(s)


# --- dunders ---


def test_len_dunder() -> None:
    assert len(Str("hello")) == 5


def test_getitem_dunder() -> None:
    assert Str("hello")[Int(1)] == Str("e")


def test_iter_yields_str_chars() -> None:
    chars = list(Str("hi"))
    assert chars == [Str("h"), Str("i")]


def test_contains_dunder_true() -> None:
    assert Str("e") in Str("hello")


def test_contains_dunder_false() -> None:
    assert Str("z") not in Str("hello")


def test_mul_repeats() -> None:
    assert Str("ab") * Int(3) == Str("ababab")


def test_lt() -> None:
    assert (Str("a") < Str("b")) is true


def test_le_equal() -> None:
    assert (Str("a") <= Str("a")) is true


def test_gt() -> None:
    assert (Str("b") > Str("a")) is true


def test_ge_equal() -> None:
    assert (Str("b") >= Str("b")) is true


# --- case ---


def test_upper() -> None:
    assert Str("hello").upper() == Str("HELLO")


def test_lower() -> None:
    assert Str("HELLO").lower() == Str("hello")


def test_capitalize() -> None:
    assert Str("hello world").capitalize() == Str("Hello world")


def test_title() -> None:
    assert Str("hello world").title() == Str("Hello World")


def test_swapcase() -> None:
    assert Str("Hello").swapcase() == Str("hELLO")


# --- strip ---


def test_strip() -> None:
    assert Str("  hi  ").strip() == Str("hi")


def test_lstrip() -> None:
    assert Str("  hi  ").lstrip() == Str("hi  ")


def test_rstrip() -> None:
    assert Str("  hi  ").rstrip() == Str("  hi")


# --- predicates ---


def test_startswith_true() -> None:
    assert Str("hello").startswith(Str("he")) is true


def test_startswith_false() -> None:
    assert Str("hello").startswith(Str("wo")) is false


def test_endswith_true() -> None:
    assert Str("hello").endswith(Str("lo")) is true


def test_endswith_false() -> None:
    assert Str("hello").endswith(Str("he")) is false


def test_isalpha_true() -> None:
    assert Str("hello").isalpha() is true


def test_isalpha_false() -> None:
    assert Str("hello1").isalpha() is false


def test_isdigit_true() -> None:
    assert Str("123").isdigit() is true


def test_isdigit_false() -> None:
    assert Str("12x").isdigit() is false


def test_isalnum_true() -> None:
    assert Str("abc123").isalnum() is true


def test_isspace_true() -> None:
    assert Str("   ").isspace() is true


def test_isupper_true() -> None:
    assert Str("HELLO").isupper() is true


def test_islower_true() -> None:
    assert Str("hello").islower() is true


# --- search / manipulation ---


def test_replace() -> None:
    assert Str("hello").replace(Str("l"), Str("r")) == Str("herro")


def test_find_found() -> None:
    assert Str("hello").find(Str("ll")) == Int(2)


def test_find_not_found() -> None:
    assert Str("hello").find(Str("xx")) == Int(-1)


def test_index_found() -> None:
    assert Str("hello").index(Str("ll")) == Int(2)


def test_index_not_found_raises() -> None:
    with pytest.raises(ValueError):
        Str("hello").index(Str("xx"))


def test_count() -> None:
    assert Str("hello").count(Str("l")) == Int(2)


def test_split_whitespace() -> None:
    assert Str("a b c").split() == [Str("a"), Str("b"), Str("c")]


def test_split_sep() -> None:
    assert Str("a,b,c").split(Str(",")) == [Str("a"), Str("b"), Str("c")]


def test_join() -> None:
    assert Str(", ").join([Str("a"), Str("b"), Str("c")]) == Str("a, b, c")


def test_int_parses_integer_string() -> None:
    from poop.types.int import Int

    assert Str("42").int() == Int(42)


def test_float_parses_float_string() -> None:
    from poop.types.float import Float

    assert Str("3.14").float() == Float(3.14)
