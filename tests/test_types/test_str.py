from typing import Any

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


def test_includes_non_value_argument_raises_faithful_typeerror() -> None:
    # A non-`_value` argument (List) must reach str.__contains__ raw and raise
    # the faithful TypeError, not leak the internal `_value` name through
    # dispatch. Mirrors CPython's `[1] in "hello"`.
    with pytest.raises(TypeError, match="requires string as left operand"):
        Str("hello").includes(List(Int(1)))  # ty: ignore[invalid-argument-type]


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


def test_startswith_tuple_with_non_str_raises() -> None:
    # CPython raises "tuple for startswith must only contain str"; POOP must
    # not silently stringify the Int member.
    with pytest.raises(TypeError):
        Str("abc").startswith(Tuple(Str("z"), Int(5)))


def test_endswith_tuple_with_non_str_raises() -> None:
    with pytest.raises(TypeError):
        Str("abc").endswith(Tuple(Str("z"), Int(5)))


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
    result = Str(", ").join(List(Str("a"), Str("b"), Str("c")))
    assert isinstance(result, Str)
    assert result == Str("a, b, c")


def test_join_rejects_non_str_parts() -> None:
    # CPython raises TypeError rather than silently stringifying non-str
    # parts; POOP must not coerce Int/Bytes via str(p) into the result.
    with pytest.raises(TypeError, match="expected str instance"):
        Str("-").join(List(Int(1), Int(2)))


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


def test_ordering_with_foreign_operand_raises_typeerror() -> None:
    # Proposal 164: a foreign operand answers CPython's TypeError, not a
    # leaking AttributeError from a missing `other._value`.
    with pytest.raises(TypeError):
        _ = Str("a") < Int(1)
    with pytest.raises(TypeError):
        _ = Str("a") >= List(Int(1))


_BAD: Any = List(Int(1), Int(2))


@pytest.mark.parametrize(
    "call, exc",
    [
        pytest.param(lambda: Str("abc").count(_BAD), TypeError, id="count"),
        pytest.param(lambda: Str("abc").find(_BAD), TypeError, id="find"),
        pytest.param(lambda: Str("abc").index(_BAD), TypeError, id="index"),
        pytest.param(lambda: Str("abc").rfind(_BAD), TypeError, id="rfind"),
        pytest.param(lambda: Str("abc").rindex(_BAD), TypeError, id="rindex"),
        pytest.param(
            lambda: Str("abc").replace(_BAD, Str("x")), TypeError, id="replace_old"
        ),
        pytest.param(
            lambda: Str("abc").replace(Str("a"), _BAD), TypeError, id="replace_new"
        ),
        pytest.param(lambda: Str("abc").center(_BAD), TypeError, id="center_width"),
        pytest.param(
            lambda: Str("abc").center(Int(5), _BAD), TypeError, id="center_fill"
        ),
        pytest.param(lambda: Str("abc").ljust(_BAD), TypeError, id="ljust"),
        pytest.param(lambda: Str("abc").rjust(_BAD), TypeError, id="rjust"),
        pytest.param(lambda: Str("abc").zfill(_BAD), TypeError, id="zfill"),
        pytest.param(lambda: Str("abc").partition(_BAD), TypeError, id="partition"),
        pytest.param(lambda: Str("abc").rpartition(_BAD), TypeError, id="rpartition"),
        pytest.param(
            lambda: Str("abc").removeprefix(_BAD), TypeError, id="removeprefix"
        ),
        pytest.param(
            lambda: Str("abc").removesuffix(_BAD), TypeError, id="removesuffix"
        ),
        pytest.param(lambda: Str("abc").strip(_BAD), TypeError, id="strip"),
        pytest.param(lambda: Str("abc").lstrip(_BAD), TypeError, id="lstrip"),
        pytest.param(lambda: Str("abc").rstrip(_BAD), TypeError, id="rstrip"),
        pytest.param(lambda: Str("abc").split(_BAD), TypeError, id="split"),
        pytest.param(lambda: Str("abc").rsplit(_BAD), TypeError, id="rsplit"),
        pytest.param(
            lambda: Str("abc").find(Str("a"), _BAD), TypeError, id="find_start"
        ),
    ],
)
def test_str_wrong_type_arg_is_faithful_not_value_leak(call, exc) -> None:
    # proposals.md item 9: a mandatory argument that carries no `_value` (a
    # List) must reach the underlying Python method raw and raise the faithful
    # exception, never leak the internal `#_value` name through dispatch.
    with pytest.raises(exc) as info:
        call()
    message = str(info.value)
    assert "_value" not in message
    assert "does not understand" not in message


def test_str_max_with_key_and_default() -> None:
    from poop.types.string import Str

    # key selects the char by a transform; default is returned for empty input.
    assert Str("abc").max(key=lambda c: -ord(c._value)) == Str("a")
    assert Str("").max(default=Str("z")) == Str("z")


def test_str_le_against_foreign_raises() -> None:
    import pytest

    from poop.types.int import Int
    from poop.types.string import Str

    with pytest.raises(TypeError):
        _ = Str("a") <= Int(1)
