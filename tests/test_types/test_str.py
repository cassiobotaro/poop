from typing import Any

import pytest

from poop import Interpreter
from poop.errors import PoopError
from poop.transformers.float import _poop_float_from
from poop.transformers.int import _poop_int_from
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.frozen_dict import FrozenDict
from poop.types.int import Int
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
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


def test_includes_refuses_a_non_text_argument_in_poops_words() -> None:
    # Was left to CPython as "the faithful TypeError". `includes`
    # is the substitute `no_in` points at, and `'in <string>' requires string as
    # left operand, not int` quotes the banned operator in its Python spelling.
    with pytest.raises(TypeError, match="#includes expects a str"):
        Str("hello").includes(List(Int(1)))  # ty: ignore[invalid-argument-type]


def test_reversed_answers_a_str() -> None:
    # Every other receiver answers its own kind, and `slice`/`at` on a Str
    # already answer a Str — a List of characters made `reversed` the one
    # message on this receiver that changed the type.
    assert Str("hello").reversed() == Str("olleh")


def test_reversed_composes_with_the_rest_of_the_string_protocol() -> None:
    assert Str("abc").reversed().upper() == Str("CBA")


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


# startswith/endswith with a tuple of prefixes


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


# str.format template method


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
    # A refusal rather than a silent `str(p)` — and POOP's sentence, naming
    # the message, where CPython's `sequence item 0: expected str instance,
    # int found` describes a position in a Python sequence.
    with pytest.raises(TypeError, match="#join expects a str, got an int"):
        Str("-").join(List(Int(1), Int(2)))


def test_int_parses_integer_string() -> None:
    assert _poop_int_from(Str("42")) == Int(42)


def test_float_parses_float_string() -> None:
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


def test_ord_refuses_a_receiver_that_is_not_one_character() -> None:
    with pytest.raises(TypeError, match="#ord expects a single character"):
        Str("ab").ord()


def test_ord_returns_code_point() -> None:
    assert Str("A").ord() == Int(65)


def test_slice_with_step() -> None:
    assert Str("abcdef").slice(Int(0), Int(6), Int(2)) == Str("ace")


def test_slice_open_ended_with_none_stop() -> None:
    # A POOP `none` stop means "to the end" (obj[2:]).
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


def test_input_at_end_of_input_is_worded_as_poop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`EOF when reading a line` names a condition, not a message.

    A pipe rather than a terminal is enough to reach it —
    `examples/basics/greet.py` answered exactly that with its stdin closed.
    """

    def fake_input(prompt: str) -> str:
        raise EOFError("EOF when reading a line")

    monkeypatch.setattr("builtins.input", fake_input)
    with pytest.raises(EOFError, match="^there is no more input to read$"):
        Str("Name: ").input()


def test_the_end_of_input_can_be_caught_by_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The mirror is what makes `except_(EOFError, …)` spellable at all: the
    # only I/O POOP has was the only failure it could not handle by name.
    def fake_input(prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)
    with pytest.raises(MIRRORS["EOFError"]):
        Str("Name: ").input()


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


# --- New: optional parameters ---


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


def test_ordering_with_foreign_operand_raises_typeerror() -> None:
    # A foreign operand answers CPython's TypeError, not a
    # leaking AttributeError from a missing `other._value`.
    with pytest.raises(TypeError):
        _ = Str("a") < Int(1)
    with pytest.raises(TypeError):
        _ = Str("a") >= List(Int(1))


_BAD: Any = List(Int(1), Int(2))
# The affix case the proposal named: `"a".startswith(1)` used to answer
# `int does not understand #_items`.
_BAD_INT: Any = Int(1)


@pytest.mark.parametrize(
    "call, exc",
    [
        pytest.param(lambda: Str("abc") + _BAD, TypeError, id="add"),
        pytest.param(lambda: Str("abc").startswith(_BAD), TypeError, id="startswith"),
        pytest.param(lambda: Str("abc").endswith(_BAD), TypeError, id="endswith"),
        pytest.param(
            lambda: Str("abc").startswith(_BAD_INT), TypeError, id="startswith_int"
        ),
        pytest.param(
            lambda: Str("abc").endswith(_BAD_INT), TypeError, id="endswith_int"
        ),
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
    # A mandatory argument that carries no `_value` (a
    # List) must reach the underlying Python method raw and raise the faithful
    # exception, never leak the internal `#_value` name through dispatch.
    with pytest.raises(exc) as info:
        call()
    message = str(info.value)
    assert "_value" not in message
    assert "does not understand" not in message


def test_str_max_with_key_and_default() -> None:
    # key selects the char by a transform; default is returned for empty input.
    assert Str("abc").max(key=lambda c: -ord(c._value)) == Str("a")
    assert Str("").max(default=Str("z")) == Str("z")


def test_str_le_against_foreign_raises() -> None:
    with pytest.raises(TypeError):
        _ = Str("a") <= Int(1)


# --- a format field must not reach attributes or items ---


@pytest.mark.parametrize(
    ("template", "args"),
    [
        pytest.param("{0.__class__}", (Int(5),), id="dunder_attribute"),
        pytest.param("{0.real}", (Int(5),), id="plain_attribute"),
        pytest.param("{0[0]}", (List(Int(1), Int(2)),), id="item"),
        pytest.param("{0[a]}", (Dict(),), id="mapping_item"),
        # A nested spec is parsed again at format time, so the same access
        # smuggles through unless the check recurses.
        pytest.param("{0:{1.__class__}}", (Int(1), Int(2)), id="nested_spec"),
    ],
)
def test_format_field_access_is_forbidden(template: str, args: tuple) -> None:
    # `str.format` reads attributes at runtime, from inside a string literal
    # no validator can see: "{0.__class__}".format(5) printed <class 'int'>.
    with pytest.raises(ValueError, match="is forbidden"):
        Str(template).format(*args)


@pytest.mark.parametrize(
    ("template", "args", "kwargs", "expected"),
    [
        pytest.param("{} {}", (Int(1), Int(2)), {}, "1 2", id="auto"),
        pytest.param("{0} {0}", (Str("x"),), {}, "x x", id="index_reuse"),
        pytest.param("{n}", (), {"n": Str("Sam")}, "Sam", id="named"),
        pytest.param("{:.2f}", (Float(1.5),), {}, "1.50", id="spec_with_a_dot"),
        pytest.param("{!r}", (Str("hi"),), {}, "'hi'", id="conversion"),
        pytest.param("{:{w}}", (Int(7),), {"w": Int(5)}, "    7", id="nested_spec"),
    ],
)
def test_format_leaves_ordinary_fields_alone(
    template: str, args: tuple, kwargs: dict, expected: str
) -> None:
    assert Str(template).format(*args, **kwargs) == Str(expected)


def test_at_accepts_a_boolean_index() -> None:
    # CPython: "ab"[True] is "b".
    assert Str("ab").at(true) == Str("b")
    assert Str("ab").at(false) == Str("a")


def test_at_with_a_foreign_index_is_faithful_not_a_value_leak() -> None:
    with pytest.raises(TypeError) as info:
        Str("ab").at(_BAD)
    assert "_value" not in str(info.value)


# the iteration protocol


def test_do_visits_each_character() -> None:
    # `no_loops` names `col.do(block)` as the substitute for `for`, and a
    # string — the most-written receiver in the language — did not answer it.
    seen: list[Str] = []
    assert Str("abc").do(lambda c: seen.append(c)) is none
    assert seen == [Str("a"), Str("b"), Str("c")]


def test_map_and_filter_yield_characters() -> None:
    assert List(*Str("abc").map(lambda c: c.upper())) == List(
        Str("A"), Str("B"), Str("C")
    )
    assert List(*Str("abc").filter(lambda c: c != Str("b"))) == List(Str("a"), Str("c"))


def test_all_any_and_reduce() -> None:
    assert Str("abc").all(lambda c: c.isalpha()) is true
    assert Str("abc").any(lambda c: c == Str("b")) is true
    assert Str("abc").reduce(Str(""), lambda acc, c: acc + c) == Str("abc")


def test_enumerate_and_zip() -> None:
    assert List(*Str("ab").enumerate()) == List(
        Tuple(Int(0), Str("a")), Tuple(Int(1), Str("b"))
    )
    assert List(*Str("ab").zip(Str("cd"))) == List(
        Tuple(Str("a"), Str("c")), Tuple(Str("b"), Str("d"))
    )


def test_sum_is_refused() -> None:
    # `sum("ab")` is a TypeError in CPython, and adding the characters up
    # would answer the string back — which is `join`'s job.
    with pytest.raises(TypeError, match="str cannot be summed"):
        Str("ab").sum()


def test_find_count_and_index_keep_their_string_meaning() -> None:
    assert Str("abc").find(Str("b")) == Int(1)
    assert Str("abcb").count(Str("b")) == Int(2)
    assert Str("abc").index(Str("c")) == Int(2)
    assert Str("abcb").rfind(Str("b")) == Int(3)
    assert Str("abcb").rindex(Str("b")) == Int(3)


@pytest.mark.parametrize("selector", ["find", "count", "index", "rfind", "rindex"])
def test_the_string_searches_refuse_a_block(selector: str) -> None:
    # Arriving from `[1, 2].find(block)`, a reader writes a block here.
    # CPython answered `find() argument 1 must be str, not function`. The
    # `r`-prefixed pair is the same message read from the other end and was
    # left on CPython's wording, so one letter changed the vocabulary.
    with pytest.raises(
        TypeError,
        match=f"^str's #{selector} searches for a substring — "
        "it takes the text to look for, not a block$",
    ):
        getattr(Str("abc"), selector)(lambda c: c == Str("b"))


# --- the template surface answers for its own failures ---
#
# `"{}".format(...)` is POOP's documented template surface (f-strings are
# banned), and all five of its failure modes were CPython's.


def test_a_missing_name_says_what_the_template_asked_for() -> None:
    # `KeyError: 'a'` is a bare repr with nothing to say a lookup failed —
    # the shape `_at.py` was written to close for a missing dict key.
    with pytest.raises(KeyError, match="the template asks for 'a'"):
        Str("{a}").format(b=Int(1))


def test_a_missing_name_lists_what_it_was_given() -> None:
    with pytest.raises(KeyError, match="which no argument named: b, c"):
        Str("{a}").format(b=Int(1), c=Int(2))
    with pytest.raises(KeyError, match="which no argument named it"):
        Str("{a}").format()


def test_a_missing_position_counts_the_values_it_got() -> None:
    # `Replacement index 0 out of range for positional args tuple` describes
    # Python's calling convention.
    with pytest.raises(IndexError, match="asks for more than the 0 values"):
        Str("{}").format()
    with pytest.raises(IndexError, match="asks for more than the 1 value it"):
        Str("{}{}").format(Int(1))


def test_a_spec_the_value_cannot_take_names_the_value() -> None:
    # `Unknown format code 'd' for object of type 'str'` names the
    # type-level protocol `_message.py` rewrites everywhere else.
    with pytest.raises(ValueError, match="^a str cannot be formatted with 'd'$"):
        Str("{:d}").format(Str("a"))
    with pytest.raises(ValueError, match="^an int cannot be formatted with 's'$"):
        Str("{:s}").format(Int(5))


def test_an_unmatched_brace_calls_it_a_template() -> None:
    # `format string` is Python's name for what POOP calls a template.
    with pytest.raises(ValueError, match="^Single '{' encountered in template$"):
        Str("{").format()


def test_the_field_access_ban_still_answers_its_own_refusal() -> None:
    # POOP's own ValueError passes through the rewording untouched.
    with pytest.raises(ValueError, match="is forbidden — a format field"):
        Str("{0.__class__}").format(Int(5))


def test_a_template_that_works_is_untouched() -> None:
    assert Str("{} and {b}").format(Int(1), b=Str("x")) == Str("1 and x")


# Three of `Str`'s own leaked the same shape, and one of them was
# the sharpest sentence in the family: `includes` is the substitute `no_in`
# points at, and its refusal quoted the banned operator in Python's spelling.
def test_includes_does_not_quote_the_banned_operator() -> None:
    with pytest.raises(TypeError, match="#includes expects a str") as info:
        Str("abc").includes(Int(5))  # ty: ignore[invalid-argument-type]
    assert "in <string>" not in str(info.value)


@pytest.mark.parametrize("selector", ["strip", "lstrip", "rstrip"])
def test_the_strip_family_names_the_message_as_a_message(selector: str) -> None:
    # `strip arg must be None or str` names the message as a bare word and its
    # own default in one breath — and `None` is a value POOP spells `none`.
    with pytest.raises(TypeError, match=f"#{selector} expects a str") as info:
        getattr(Str("abc"), selector)(Int(5))
    assert "arg must be" not in str(info.value)


@pytest.mark.parametrize("selector", ["split", "rsplit"])
def test_the_split_pair_names_the_message_as_a_message(selector: str) -> None:
    # `must be str or None, not int` names no message at all, where the byte
    # twins already answered `#split expects bytes, got an int`.
    with pytest.raises(TypeError, match=f"^#{selector} expects a str, got an int$"):
        getattr(Str("a,b"), selector)(Int(5))


@pytest.mark.parametrize("selector", ["split", "rsplit"])
def test_the_split_pair_still_takes_no_separator(selector: str) -> None:
    assert getattr(Str("a b"), selector)() == List(Str("a"), Str("b"))
    assert getattr(Str("a b"), selector)(none) == List(Str("a"), Str("b"))


@pytest.mark.parametrize("selector", ["split", "rsplit"])
def test_the_split_pair_names_its_maxsplit(selector: str) -> None:
    # `'str' object cannot be interpreted as an integer` names neither the
    # message nor the argument.
    wanted = f"^#{selector}'s maxsplit must be an int, got a str$"
    with pytest.raises(TypeError, match=wanted):
        getattr(Str("a,b"), selector)(Str(","), Str("x"))
    whole = List(Str("a"), Str("b"))
    assert getattr(Str("a,b"), selector)(Str(","), none) == whole
    assert getattr(Str("a,b"), selector)(Str(","), Int(1)) == whole


@pytest.mark.parametrize("selector", ["partition", "rpartition"])
def test_the_partition_pair_names_the_message_as_a_message(selector: str) -> None:
    # `must be str, not int` names no message at all.
    with pytest.raises(TypeError, match=f"^#{selector} expects a str, got an int$"):
        getattr(Str("a,b"), selector)(Int(5))
    with pytest.raises(TypeError, match=f"^#{selector} expects a str, got a bytes$"):
        getattr(Str("a,b"), selector)(Bytes(b","))


def test_the_strip_family_still_takes_no_argument() -> None:
    assert Str("  a  ").strip() == Str("a")
    assert Str("xxaxx").strip(Str("x")) == Str("a")


@pytest.mark.parametrize("selector", ["center", "ljust", "rjust"])
@pytest.mark.parametrize(
    ("fill", "expected"),
    [
        (Int(1), "#{} expects one character, got an int"),
        (Str("xy"), "#{} expects one character, got a str of length 2"),
        (Str(""), "#{} expects one character, got a str of length 0"),
    ],
    ids=["int", "two-characters", "empty"],
)
def test_a_wrong_fill_is_refused_in_poops_words(
    selector: str, fill: object, expected: str
) -> None:
    """CPython answered `The fill character must be ...` for all three."""
    with pytest.raises(TypeError, match=f"^{expected.format(selector)}$"):
        getattr(Str("ab"), selector)(Int(6), fill)


def test_replace_names_its_count() -> None:
    # `'str' object cannot be interpreted as an integer`, the sentence `an_int`
    # replaces, reached this one argument unguarded.
    wrong: Any = Str("x")
    with pytest.raises(TypeError, match="^#replace's count must be an int, got a str$"):
        Str("abc").replace(Str("a"), Str("b"), wrong)
    assert Str("aa").replace(Str("a"), Str("b"), none) == Str("bb")
    assert Str("aa").replace(Str("a"), Str("b"), Int(1)) == Str("ba")


# --- format_map, maketrans and translate: the last three names a mechanical
# diff of `str`'s public methods against `Str` found missing. Each scenario in
# openspec/specs/str-type/spec.md is pinned here.


def _run(source: str, capsys: pytest.CaptureFixture[str]) -> str:
    Interpreter().run_source(source + "\n")
    return capsys.readouterr().out.rstrip("\n")


def _failure(source: str) -> str:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source + "\n")
    return str(info.value)


def test_format_map_fills_named_fields_from_a_mapping(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run('"{a}-{b}".format_map({"a": 1, "b": 2}).print()', capsys) == "1-2"
    assert _run('"{x:.2f}".format_map({"x": 1.5}).print()', capsys) == "1.50"


def test_format_map_takes_every_poop_mapping() -> None:
    table = Dict()
    table.at_put(Str("a"), Int(1))
    assert Str("{a}").format_map(table) == Str("1")
    assert Str("{a}").format_map(FrozenDict._wrapping({Str("a"): Int(1)})) == Str("1")
    assert Str("{a}").format_map(MappingProxy(table)) == Str("1")


def test_format_map_keeps_the_field_access_ban() -> None:
    # The same refusal `format` gives for `"{0.__class__}".format(1)`.
    with pytest.raises(ValueError, match="is forbidden — a format field") as info:
        Str("{a.__class__}").format_map(Dict())
    with pytest.raises(ValueError) as twin:
        Str("{0.__class__}").format(Int(1))
    assert str(info.value).replace("{a.", "{0.") == str(twin.value)


def test_format_map_words_a_missing_name_as_format_does() -> None:
    assert _failure('"{a}".format_map({})').startswith(
        "KeyError: the template asks for 'a', which no argument named"
    )
    assert _failure('"{a}".format_map({"b": 1, "c": 2})') == (
        "KeyError: the template asks for 'a', which no argument named: b, c (line 1)"
    )


@pytest.mark.parametrize(
    ("source", "got"),
    [('"{a}".format_map(5)', "an int"), ('"{a}".format_map([1])', "a list")],
)
def test_format_map_refuses_a_non_mapping_in_poops_words(source: str, got: str) -> None:
    assert (
        _failure(source)
        == f"TypeError: #format_map expects a mapping, got {got} (line 1)"
    )


def test_format_map_keeps_cpythons_sentence_for_a_positional_field() -> None:
    # `Format string contains positional fields` names nothing POOP forbids.
    assert _failure('"{0}".format_map({"a": 1})') == (
        "ValueError: Format string contains positional fields (line 1)"
    )


def test_maketrans_maps_two_strings_position_by_position(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run('str.maketrans("abc", "xyz").print()', capsys) == (
        "{97: 120, 98: 121, 99: 122}"
    )


def test_maketrans_third_string_deletes(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run('str.maketrans("a", "b", "c").print()', capsys) == "{97: 98, 99: None}"


def test_maketrans_one_mapping_converts_character_keys(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run('str.maketrans({"a": "x", 98: None}).print()', capsys) == (
        "{97: 'x', 98: None}"
    )


def test_maketrans_is_static_so_an_instance_answers_it_too() -> None:
    # CPython's is a staticmethod: `"".maketrans("a", "b")` works there.
    table = Str("").maketrans(Str("a"), Str("b"))
    assert table.is_instance(Dict) == true
    assert table.at(Int(97)) == Int(98)


def test_maketrans_answers_poop_values() -> None:
    table = Str.maketrans(Str("a"), Str("b"), Str("c"))
    assert table.at(Int(99)) is none


def test_maketrans_keeps_cpythons_value_refusals() -> None:
    # Neither sentence names a construct POOP forbids.
    assert _failure('str.maketrans("ab", "xyz")') == (
        "ValueError: the first two maketrans arguments must have equal length (line 1)"
    )
    assert _failure('str.maketrans({"ab": "x"})') == (
        "ValueError: string keys in translatetable must be of length 1 (line 1)"
    )


def test_maketrans_refuses_a_single_non_mapping_in_poops_words() -> None:
    # CPython: `if you give only one argument to maketrans it must be a dict`,
    # the message spelt as a call.
    assert _failure("str.maketrans(5)") == (
        "TypeError: #maketrans expects a mapping, got an int (line 1)"
    )
    assert _failure('str.maketrans("a", 5)') == (
        "TypeError: #maketrans expects a str, got an int (line 1)"
    )
    assert _failure('str.maketrans("a", "b", 5)') == (
        "TypeError: #maketrans expects a str, got an int (line 1)"
    )


def test_translate_reads_a_maketrans_table(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run('"abc".translate(str.maketrans("abc", "xyz")).print()', capsys) == "xyz"


def test_translate_deletes_on_none_and_leaves_a_miss(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run('"a-b".translate({45: None}).print()', capsys) == "ab"
    assert _run('"abc".translate({97: 120}).print()', capsys) == "xbc"


def test_translate_refuses_a_non_table_in_poops_words() -> None:
    assert _failure('"abc".translate(5)') == (
        "TypeError: #translate expects a mapping or a sequence, got an int (line 1)"
    )


def test_translate_keeps_cpythons_sentence_for_a_mapped_value() -> None:
    assert _failure('"abc".translate({97: 5.5})') == (
        "TypeError: character mapping must return integer, None or str (line 1)"
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('"ab".index("z")', "str has no element equal to 'z'"),
        ('"ab".rindex("z")', "str has no element equal to 'z'"),
        ('"ab".index("a", 1)', "str has no element equal to 'a'"),
    ],
    ids=["index", "rindex", "bounded"],
)
def test_index_misses_in_the_familys_words(source: str, expected: str) -> None:
    # CPython's `substring not found` names neither the receiver nor the
    # value; every other sequence's `index` names both.
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source)
    assert info.value.message == f"ValueError: {expected}"


def test_find_still_answers_minus_one_on_a_miss() -> None:
    assert Str("ab").find(Str("z")) == Int(-1)
