import pytest

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
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


# startswith/endswith with a tuple of prefixes — proposal 136


def test_startswith_tuple_of_prefixes() -> None:
    assert Str("abc").startswith(Tuple(Str("a"), Str("z"))) is true
    assert Str("abc").startswith(Tuple(Str("x"), Str("z"))) is false


def test_endswith_tuple_of_suffixes() -> None:
    assert Str("abc").endswith(Tuple(Str("c"), Str("z"))) is true
    assert Str("abc").endswith(Tuple(Str("x"), Str("z"))) is false


# str.format template method — proposal 151


def test_format_positional() -> None:
    assert Str("Hello, {}!").format(Str("world")) == Str("Hello, world!")


def test_format_multiple_positional() -> None:
    assert Str("{} + {} = {}").format(Int(1), Int(2), Int(3)) == Str("1 + 2 = 3")


def test_format_named() -> None:
    assert Str("{name} is {age}").format(name=Str("Sam"), age=Int(30)) == Str(
        "Sam is 30"
    )


def test_format_with_spec() -> None:
    assert Str("{:^10}").format(Str("hi")) == Str("    hi    ")


def test_format_index_reuse() -> None:
    assert Str("{0} {0}").format(Str("x")) == Str("x x")


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

    result = _poop_float_from(Str("3.14"))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.14)


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


def test_slice_open_ended_with_none_stop() -> None:
    # proposal 143: a POOP `none` stop means "to the end" (obj[2:]).
    assert Str("hello").slice(Int(2), none) == Str("llo")


def test_slice_open_ended_with_none_step() -> None:
    assert Str("abcdef").slice(Int(1), Int(5), none) == Str("bcde")


def test_slice_stop_omitted_means_open_ended() -> None:
    assert Str("hello").slice(Int(2)) == Str("llo")


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


# --- base64 (decode-only on Str; encode lives on Bytes) ---


def test_b64decode_from_str() -> None:
    from poop.types.bytes import Bytes

    result = Str("YWJj").b64decode()
    assert isinstance(result, Bytes)
    assert result == Bytes(b"abc")


def test_b16decode_from_str() -> None:
    from poop.types.bytes import Bytes

    assert Str("616263").b16decode() == Bytes(b"abc")


def test_b32decode_from_str() -> None:
    from poop.types.bytes import Bytes

    assert Str("MFRGG===").b32decode() == Bytes(b"abc")


def test_b32hexdecode_from_str() -> None:
    from poop.types.bytes import Bytes

    encoded = Bytes(b"hello").b32hexencode()
    assert encoded.decode(Str("ascii")).b32hexdecode() == Bytes(b"hello")


def test_standard_b64decode_from_str() -> None:
    from poop.types.bytes import Bytes

    assert Str("YWJj").standard_b64decode() == Bytes(b"abc")


def test_urlsafe_b64decode_from_str() -> None:
    from poop.types.bytes import Bytes

    encoded = Bytes(b"\xfb\xff\xfe").urlsafe_b64encode()
    decoded = encoded.decode(Str("ascii")).urlsafe_b64decode()
    assert decoded == Bytes(b"\xfb\xff\xfe")


def test_a85decode_from_str() -> None:
    from poop.types.bytes import Bytes

    encoded = Bytes(b"hello").a85encode()
    assert encoded.decode(Str("ascii")).a85decode() == Bytes(b"hello")


def test_b85decode_from_str() -> None:
    from poop.types.bytes import Bytes

    encoded = Bytes(b"hello").b85encode()
    assert encoded.decode(Str("ascii")).b85decode() == Bytes(b"hello")


def test_z85decode_from_str() -> None:
    from poop.types.bytes import Bytes

    encoded = Bytes(b"abcd").z85encode()
    assert encoded.decode(Str("ascii")).z85decode() == Bytes(b"abcd")


# --- New: optional parameters (proposals 32-39, v1.2.0) ---


def test_strip_with_chars_arg() -> None:
    assert Str("###hi###").strip(Str("#")) == Str("hi")


def test_lstrip_with_chars_arg() -> None:
    assert Str("xxhi").lstrip(Str("x")) == Str("hi")


def test_rstrip_with_chars_arg() -> None:
    assert Str("hixx").rstrip(Str("x")) == Str("hi")


def test_strip_with_poop_none_chars() -> None:
    assert Str("  hi  ").strip(chars=none) == Str("hi")
    assert Str("  hi  ").lstrip(chars=none) == Str("hi  ")
    assert Str("  hi  ").rstrip(chars=none) == Str("  hi")


def test_split_with_maxsplit() -> None:
    assert Str("a:b:c:d").split(Str(":"), Int(2)) == List(
        Str("a"), Str("b"), Str("c:d")
    )


def test_split_with_poop_none_maxsplit() -> None:
    assert Str("a:b:c").split(Str(":"), maxsplit=none) == List(
        Str("a"), Str("b"), Str("c")
    )


def test_rsplit_with_maxsplit() -> None:
    assert Str("a:b:c:d").rsplit(Str(":"), Int(2)) == List(
        Str("a:b"), Str("c"), Str("d")
    )


def test_rsplit_default_sep() -> None:
    assert Str("a b c").rsplit() == List(Str("a"), Str("b"), Str("c"))


def test_find_with_start() -> None:
    assert Str("hello hello").find(Str("hello"), Int(1)) == Int(6)


def test_find_with_start_and_end() -> None:
    assert Str("hello hello").find(Str("hello"), Int(0), Int(5)) == Int(0)
    assert Str("hello hello").find(Str("hello"), Int(0), Int(4)) == Int(-1)


def test_index_with_start() -> None:
    assert Str("hello hello").index(Str("hello"), Int(1)) == Int(6)


def test_index_with_start_and_end_not_found_raises() -> None:
    with pytest.raises(ValueError):
        Str("hello hello").index(Str("hello"), Int(0), Int(4))


def test_count_with_start_and_end() -> None:
    assert Str("hello hello hello").count(Str("hello"), Int(6)) == Int(2)
    assert Str("hello hello hello").count(Str("hello"), Int(6), Int(11)) == Int(1)


def test_rfind_with_start() -> None:
    assert Str("hello hello").rfind(Str("hello"), Int(0), Int(5)) == Int(0)


def test_rindex_with_start() -> None:
    assert Str("hello hello").rindex(Str("hello"), Int(0), Int(5)) == Int(0)


# --- New: optional parameters (proposals 43-44, v1.1.2) ---


def test_startswith_with_start() -> None:
    assert Str("hello world").startswith(Str("world"), Int(6)) is true


def test_startswith_with_start_and_end() -> None:
    assert Str("hello world").startswith(Str("world"), Int(6), Int(11)) is true
    assert Str("hello world").startswith(Str("world"), Int(0), Int(5)) is false


def test_endswith_with_start() -> None:
    assert Str("hello world").endswith(Str("hello"), Int(0), Int(5)) is true


def test_endswith_with_poop_none_bounds() -> None:
    assert Str("hello").endswith(Str("lo"), start=none, end=none) is true


def test_replace_with_count() -> None:
    assert Str("aaa").replace(Str("a"), Str("b"), Int(1)) == Str("baa")
    assert Str("aaaa").replace(Str("a"), Str("b"), Int(2)) == Str("bbaa")


def test_replace_with_poop_none_count() -> None:
    assert Str("aaa").replace(Str("a"), Str("b"), count=none) == Str("bbb")


def test_str_b64decode_with_validate() -> None:
    assert Str("YWJj").b64decode(validate=true) == Bytes(b"abc")


def test_str_b64decode_validate_rejects_garbage() -> None:
    with pytest.raises(Exception):  # noqa: B017, PT011 — binascii.Error
        Str("YW Jj").b64decode(validate=true)


def test_str_b64decode_altchars() -> None:
    encoded = Bytes(b"\xfb\xff").b64encode(altchars=Bytes(b"-_"))
    assert Str(encoded._value.decode()).b64decode(altchars=Str("-_")) == Bytes(
        b"\xfb\xff"
    )


def test_str_b16decode_casefold() -> None:
    assert Str("6162").b16decode(casefold=true) == Bytes(b"ab")


def test_str_b32decode_casefold_and_map01() -> None:
    encoded = Bytes(b"ab").b32encode()._value.decode().lower()
    assert Str(encoded).b32decode(casefold=true) == Bytes(b"ab")
    swapped = Str(encoded.replace("o", "0"))
    assert swapped.b32decode(casefold=true, map01=Str("L")) == Bytes(b"ab")


def test_str_b32hexdecode_casefold() -> None:
    encoded = Bytes(b"ab").b32hexencode()._value.decode().lower()
    assert Str(encoded).b32hexdecode(casefold=true) == Bytes(b"ab")


def test_str_a85decode_with_kwargs() -> None:
    encoded = Bytes(b"hello").a85encode()._value.decode()
    spaced = Str(" " + encoded + " ")
    assert spaced.a85decode(ignorechars=Str(" ")) == Bytes(b"hello")


def test_mod_scalar() -> None:
    assert Str("v %s") % Int(5) == Str("v 5")


def test_mod_single_element_tuple() -> None:
    assert Str("v %s") % Tuple(Int(5)) == Str("v 5")


def test_mod_multiple_tuple() -> None:
    assert Str("%s/%s") % Tuple(Str("a"), Str("b")) == Str("a/b")


def test_mod_numeric_format() -> None:
    assert Str("%d items at $%.2f") % Tuple(Int(3), Float(1.5)) == Str(
        "3 items at $1.50"
    )


def test_mod_mapping() -> None:
    mapping = Dict()
    mapping.at_put(Str("name"), Str("Ana"))
    mapping.at_put(Str("age"), Int(30))
    assert Str("%(name)s is %(age)d") % mapping == Str("Ana is 30")


def test_mod_percent_literal() -> None:
    assert Str("100%% done") % Tuple() == Str("100% done")


def test_mod_type_mismatch_raises() -> None:
    with pytest.raises(TypeError):
        _ = Str("got %d") % Str("abc")
