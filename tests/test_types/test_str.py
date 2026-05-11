import pytest

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple


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
    from poop.types.list import List

    assert Str("hello").reversed() == List(
        Str("o"), Str("l"), Str("l"), Str("e"), Str("h")
    )


def test_reversed_empty() -> None:
    from poop.types.list import List

    assert Str("").reversed() == List()


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


def test_str_str_returns_raw_value() -> None:
    assert str(Str("hello")) == "hello"


def test_str_repr_wraps_in_quotes() -> None:
    assert repr(Str("hello")) == "'hello'"


def test_str_repr_eval_roundtrip() -> None:
    assert eval(repr(Str("it's"))) == "it's"  # noqa: S307


# --- dunders ---


def test_len_dunder() -> None:
    assert len(Str("hello")) == 5


def test_at_returns_second_char() -> None:
    assert Str("hello").at(Int(1)) == Str("e")


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
    assert Str("a b c").split() == List(Str("a"), Str("b"), Str("c"))


def test_split_sep() -> None:
    assert Str("a,b,c").split(Str(",")) == List(Str("a"), Str("b"), Str("c"))


def test_join() -> None:
    assert Str(", ").join(List(Str("a"), Str("b"), Str("c"))) == Str("a, b, c")


def test_int_parses_integer_string() -> None:
    from poop.transformers.int import _poop_int_from

    assert _poop_int_from(Str("42")) == Int(42)


def test_float_parses_float_string() -> None:
    from poop.transformers.float import _poop_float_from

    assert _poop_float_from(Str("3.14")) == Float(3.14)


def test_casefold() -> None:
    assert Str("Hello WORLD").casefold() == Str("hello world")


def test_center_no_fillchar() -> None:
    assert Str("hi").center(Int(6)) == Str("  hi  ")


def test_center_with_fillchar() -> None:
    assert Str("hi").center(Int(6), Str("*")) == Str("**hi**")


def test_encode_returns_bytes() -> None:
    assert Str("hello").encode(Str("utf-8")) == Bytes(b"hello")


def test_expandtabs_default() -> None:
    assert Str("a\tb").expandtabs() == Str("a       b")


def test_expandtabs_with_size() -> None:
    assert Str("a\tb").expandtabs(Int(4)) == Str("a   b")


def test_isascii_true() -> None:
    assert Str("hello").isascii() is true


def test_isascii_false() -> None:
    assert Str("héllo").isascii() is false


def test_isdecimal_true() -> None:
    assert Str("123").isdecimal() is true


def test_isdecimal_false() -> None:
    assert Str("12.3").isdecimal() is false


def test_isidentifier_true() -> None:
    assert Str("my_var").isidentifier() is true


def test_isidentifier_false() -> None:
    assert Str("1var").isidentifier() is false


def test_isnumeric_true() -> None:
    assert Str("123").isnumeric() is true


def test_isprintable_true() -> None:
    assert Str("hello").isprintable() is true


def test_isprintable_false() -> None:
    assert Str("hello\x00").isprintable() is false


def test_istitle_true() -> None:
    assert Str("Hello World").istitle() is true


def test_istitle_false() -> None:
    assert Str("hello world").istitle() is false


def test_ljust() -> None:
    assert Str("hi").ljust(Int(5)) == Str("hi   ")


def test_ljust_with_fillchar() -> None:
    assert Str("hi").ljust(Int(5), Str("-")) == Str("hi---")


def test_rjust() -> None:
    assert Str("hi").rjust(Int(5)) == Str("   hi")


def test_rjust_with_fillchar() -> None:
    assert Str("hi").rjust(Int(5), Str("-")) == Str("---hi")


def test_zfill() -> None:
    assert Str("42").zfill(Int(5)) == Str("00042")


def test_partition() -> None:
    assert Str("hello world foo").partition(Str(" ")) == Tuple(
        Str("hello"), Str(" "), Str("world foo")
    )


def test_rpartition() -> None:
    assert Str("hello world foo").rpartition(Str(" ")) == Tuple(
        Str("hello world"), Str(" "), Str("foo")
    )


def test_removeprefix() -> None:
    assert Str("hello world").removeprefix(Str("hello ")) == Str("world")


def test_removeprefix_no_match() -> None:
    assert Str("hello world").removeprefix(Str("bye")) == Str("hello world")


def test_removesuffix() -> None:
    assert Str("hello world").removesuffix(Str(" world")) == Str("hello")


def test_removesuffix_no_match() -> None:
    assert Str("hello world").removesuffix(Str("bye")) == Str("hello world")


def test_rfind_found() -> None:
    assert Str("hello hello").rfind(Str("hello")) == Int(6)


def test_rfind_not_found() -> None:
    assert Str("hello").rfind(Str("xyz")) == Int(-1)


def test_rindex_found() -> None:
    assert Str("hello hello").rindex(Str("hello")) == Int(6)


def test_rindex_not_found_raises() -> None:
    with pytest.raises(ValueError):
        Str("hello").rindex(Str("xyz"))


def test_rsplit() -> None:
    assert Str("a b c").rsplit(Str(" ")) == List(Str("a"), Str("b"), Str("c"))


def test_splitlines() -> None:
    assert Str("a\nb\nc").splitlines() == List(Str("a"), Str("b"), Str("c"))


def test_ord_returns_code_point() -> None:
    assert Str("A").ord() == Int(65)


def test_slice_with_step() -> None:
    assert Str("abcdef").slice(Int(0), Int(6), Int(2)) == Str("ace")


def test_contains_non_str_returns_false() -> None:
    assert (Int(1) in Str("123")) is False


def test_rmul_returns_repeated_string() -> None:
    assert Str("ab").__rmul__(Int(3)) == Str("ababab")


def test_eq_with_non_str_returns_false() -> None:
    assert Str("hello").__eq__(Int(1)) is false


def test_ne_with_non_str_returns_true() -> None:
    assert Str("hello").__ne__(Int(1)) is true


def test_input_with_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_input(prompt: str) -> str:
        seen.append(prompt)
        return "alice"

    monkeypatch.setattr("builtins.input", fake_input)
    assert Str("Name: ").input() == Str("alice")
    assert seen == ["Name: "]


def test_input_empty_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_input(prompt: str) -> str:
        seen.append(prompt)
        return "data"

    monkeypatch.setattr("builtins.input", fake_input)
    assert Str("").input() == Str("data")
    assert seen == [""]


def test_input_returns_str_type(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "x")
    result = Str("? ").input()
    assert isinstance(result, Str)


def test_input_propagates_eof(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_eof(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    with pytest.raises(EOFError):
        Str("? ").input()


def test_methods_accept_poop_none_kwargs() -> None:
    from poop.types.none import none

    assert Str("hi").split(sep=none) == List(Str("hi"))
    assert Str("hi").center(Int(6), fillchar=none) == Str("  hi  ")
    assert Str("hi").ljust(Int(4), fillchar=none) == Str("hi  ")
    assert Str("hi").rjust(Int(4), fillchar=none) == Str("  hi")
    assert Str("a\tb").expandtabs(tabsize=none) == Str("a       b")
