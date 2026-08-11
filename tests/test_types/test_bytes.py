from typing import Any

import pytest

from poop.parser import parse
from poop.transformers.bytes import BytesTransformer
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_empty_bytes() -> None:
    assert Bytes(b"").len() == Int(0)


def test_len() -> None:
    assert Bytes(b"abc").len() == Int(3)


def test_dunder_len() -> None:
    assert len(Bytes(b"hi")) == 2


def test_at_returns_byte_value_as_int() -> None:
    assert Bytes(b"ABC").at(Int(0)) == Int(65)
    assert Bytes(b"ABC").at(Int(1)) == Int(66)


def test_at_zero_indexed() -> None:
    assert Bytes(b"Z").at(Int(0)) == Int(90)


def test_includes_true() -> None:
    assert Bytes(b"hello").includes(Int(104)) is true  # ord('h') == 104


def test_includes_false() -> None:
    assert Bytes(b"hello").includes(Int(0)) is false


def test_includes_refuses_a_non_bytes_argument_in_poops_words() -> None:
    # Proposal 52: was left to CPython's `a bytes-like object is required, not
    # 'list'` — a sentence with no receiver, no message and no substitute, and
    # one the wording sweep could not see.
    with pytest.raises(TypeError, match="#includes expects bytes or an int"):
        Bytes(b"hello").includes(List(Int(1)))  # ty: ignore[invalid-argument-type]


def test_contains_dunder() -> None:
    b = Bytes(b"abc")
    assert Int(97) in b  # ord('a')
    assert Int(0) not in b


def test_decode_utf8() -> None:
    assert Bytes(b"hello").decode(Str("utf-8")) == Str("hello")


def test_decode_ascii() -> None:
    assert Bytes(b"hi").decode(Str("ascii")) == Str("hi")


def test_hex() -> None:
    result = Bytes(b"\xff\x00").hex()
    assert isinstance(result, Str)
    assert result == Str("ff00")


def test_do_yields_int_byte_values() -> None:
    seen: list[Int] = []
    Bytes(b"\x01\x02\x03").do(lambda b: seen.append(b))
    assert seen == [Int(1), Int(2), Int(3)]


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    result = Bytes(b"\x01\x02").map(lambda b: b)
    assert isinstance(result, Map)


def test_map_transforms_bytes() -> None:
    result = List(*Bytes(b"\x01\x02").map(lambda b: Int(b._value * 2)))
    assert result.at(Int(0)) == Int(2)
    assert result.at(Int(1)) == Int(4)


def test_iter_yields_int_byte_values() -> None:
    items = list(Bytes(b"\x0a\x0b"))
    assert items == [Int(10), Int(11)]


def test_eq_equal_bytes() -> None:
    assert Bytes(b"abc") == Bytes(b"abc")


def test_eq_different_bytes() -> None:
    assert (Bytes(b"abc") == Bytes(b"xyz")) is false


def test_ne_different_bytes() -> None:
    assert (Bytes(b"abc") != Bytes(b"xyz")) is true


def test_lt() -> None:
    assert (Bytes(b"a") < Bytes(b"b")) is true


def test_le_equal() -> None:
    assert (Bytes(b"a") <= Bytes(b"a")) is true


def test_gt() -> None:
    assert (Bytes(b"b") > Bytes(b"a")) is true


def test_ge_equal() -> None:
    assert (Bytes(b"b") >= Bytes(b"b")) is true


def test_lt_foreign_operand_raises() -> None:
    with pytest.raises(TypeError):
        Bytes(b"a") < Str("b")  # noqa: B015


def test_hashable() -> None:
    assert isinstance(hash(Bytes(b"hello")), int)


def test_equal_bytes_have_equal_hash() -> None:
    assert hash(Bytes(b"abc")) == hash(Bytes(b"abc"))


def test_bytes_can_be_dict_key() -> None:
    d = Dict()
    key = Bytes(b"key")
    d.at_put(key, Int(42))
    assert d.at(Bytes(b"key")) == Int(42)


def test_str_representation() -> None:
    assert str(Bytes(b"hi")) == "b'hi'"


def test_repr_equals_str() -> None:
    b = Bytes(b"test")
    assert repr(b) == str(b)


def test_transformer_literal() -> None:
    tree = parse('b = b"hello"')
    tree = BytesTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_bytes": Bytes}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["b"]
    assert isinstance(result, Bytes)
    assert result.len() == Int(5)


def test_transformer_empty_literal() -> None:
    tree = parse("b = b''")
    tree = BytesTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_bytes": Bytes}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["b"], Bytes)
    assert ns["b"].len() == Int(0)  # type: ignore[union-attr]


def test_transformer_does_not_affect_str_literals() -> None:
    tree = BytesTransformer().transform(parse('s = "hello"'))
    ns: dict[str, object] = {}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["s"], str)


def test_not_mutable_no_set_item() -> None:
    b = Bytes(b"abc")
    assert not hasattr(b, "at_put")


def test_capitalize() -> None:
    assert Bytes(b"hello world").capitalize() == Bytes(b"Hello world")


def test_center_no_fill() -> None:
    assert Bytes(b"hi").center(Int(6)) == Bytes(b"  hi  ")


def test_center_with_fill() -> None:
    assert Bytes(b"hi").center(Int(6), Bytes(b"*")) == Bytes(b"**hi**")


def test_count() -> None:
    assert Bytes(b"abcabc").count(Bytes(b"ab")) == Int(2)


def test_endswith_true() -> None:
    assert Bytes(b"hello").endswith(Bytes(b"lo")) is true


def test_endswith_false() -> None:
    assert Bytes(b"hello").endswith(Bytes(b"hi")) is false


def test_expandtabs_default() -> None:
    assert Bytes(b"a\tb").expandtabs() == Bytes(b"a       b")


def test_expandtabs_custom() -> None:
    assert Bytes(b"a\tb").expandtabs(Int(4)) == Bytes(b"a   b")


def test_find_found() -> None:
    assert Bytes(b"hello").find(Bytes(b"ll")) == Int(2)


def test_find_not_found() -> None:
    assert Bytes(b"hello").find(Bytes(b"xyz")) == Int(-1)


def test_index_found() -> None:
    assert Bytes(b"hello").index(Bytes(b"ll")) == Int(2)


def test_isalnum_true() -> None:
    assert Bytes(b"abc123").isalnum() is true


def test_isalnum_false() -> None:
    assert Bytes(b"abc!").isalnum() is false


def test_isalpha_true() -> None:
    assert Bytes(b"abc").isalpha() is true


def test_isalpha_false() -> None:
    assert Bytes(b"abc1").isalpha() is false


def test_isascii_true() -> None:
    assert Bytes(b"hello").isascii() is true


def test_isdigit_true() -> None:
    assert Bytes(b"123").isdigit() is true


def test_isdigit_false() -> None:
    assert Bytes(b"12a").isdigit() is false


def test_islower_true() -> None:
    assert Bytes(b"hello").islower() is true


def test_islower_false() -> None:
    assert Bytes(b"Hello").islower() is false


def test_isspace_true() -> None:
    assert Bytes(b"   ").isspace() is true


def test_isspace_false() -> None:
    assert Bytes(b" a ").isspace() is false


def test_istitle_true() -> None:
    assert Bytes(b"Hello World").istitle() is true


def test_istitle_false() -> None:
    assert Bytes(b"hello world").istitle() is false


def test_isupper_true() -> None:
    assert Bytes(b"HELLO").isupper() is true


def test_isupper_false() -> None:
    assert Bytes(b"Hello").isupper() is false


def test_join() -> None:
    parts = List(Bytes(b"a"), Bytes(b"b"), Bytes(b"c"))
    assert Bytes(b"-").join(parts) == Bytes(b"a-b-c")


def test_join_accepts_other_bytes_like() -> None:
    from poop.types.byte_array import ByteArray
    from poop.types.memory_view import MemoryView

    parts = List(Bytes(b"a"), ByteArray(bytearray(b"b")), MemoryView(memoryview(b"c")))
    assert Bytes(b"-").join(parts) == Bytes(b"a-b-c")


def test_join_non_bytes_like_raises() -> None:
    # CPython raises TypeError rather than silently dropping the str element.
    parts = List(Bytes(b"a"), Str("x"), Bytes(b"b"))
    with pytest.raises(TypeError, match="#join expects bytes"):
        Bytes(b"-").join(parts)


def test_ljust_no_fill() -> None:
    assert Bytes(b"hi").ljust(Int(5)) == Bytes(b"hi   ")


def test_ljust_with_fill() -> None:
    assert Bytes(b"hi").ljust(Int(5), Bytes(b"*")) == Bytes(b"hi***")


def test_lower() -> None:
    assert Bytes(b"HELLO").lower() == Bytes(b"hello")


def test_lstrip_default() -> None:
    assert Bytes(b"  hello").lstrip() == Bytes(b"hello")


def test_lstrip_chars() -> None:
    assert Bytes(b"xxxhello").lstrip(Bytes(b"x")) == Bytes(b"hello")


def test_partition() -> None:
    result = Bytes(b"hello world").partition(Bytes(b" "))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Bytes(b"hello")
    assert result.at(Int(1)) == Bytes(b" ")
    assert result.at(Int(2)) == Bytes(b"world")


def test_removeprefix() -> None:
    assert Bytes(b"hello").removeprefix(Bytes(b"hel")) == Bytes(b"lo")


def test_removeprefix_no_match() -> None:
    assert Bytes(b"hello").removeprefix(Bytes(b"xyz")) == Bytes(b"hello")


def test_removesuffix() -> None:
    assert Bytes(b"hello").removesuffix(Bytes(b"lo")) == Bytes(b"hel")


def test_replace() -> None:
    assert Bytes(b"aabbcc").replace(Bytes(b"bb"), Bytes(b"XX")) == Bytes(b"aaXXcc")


def test_rfind() -> None:
    assert Bytes(b"abcabc").rfind(Bytes(b"ab")) == Int(3)


def test_rfind_not_found() -> None:
    assert Bytes(b"hello").rfind(Bytes(b"xyz")) == Int(-1)


def test_rindex() -> None:
    assert Bytes(b"abcabc").rindex(Bytes(b"ab")) == Int(3)


def test_rjust_no_fill() -> None:
    assert Bytes(b"hi").rjust(Int(5)) == Bytes(b"   hi")


def test_rjust_with_fill() -> None:
    assert Bytes(b"hi").rjust(Int(5), Bytes(b"*")) == Bytes(b"***hi")


def test_rpartition() -> None:
    result = Bytes(b"hello world").rpartition(Bytes(b" "))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Bytes(b"hello")
    assert result.at(Int(2)) == Bytes(b"world")


def test_rsplit_no_sep() -> None:
    result = Bytes(b"a b c").rsplit()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_rsplit_with_sep() -> None:
    result = Bytes(b"a,b,c").rsplit(Bytes(b","))
    assert isinstance(result, List)
    assert result.at(Int(0)) == Bytes(b"a")


def test_rstrip_default() -> None:
    assert Bytes(b"hello  ").rstrip() == Bytes(b"hello")


def test_rstrip_chars() -> None:
    assert Bytes(b"helloxx").rstrip(Bytes(b"x")) == Bytes(b"hello")


def test_split_no_sep() -> None:
    result = Bytes(b"a b c").split()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_split_with_sep() -> None:
    result = Bytes(b"a,b,c").split(Bytes(b","))
    assert isinstance(result, List)
    assert result.at(Int(0)) == Bytes(b"a")
    assert result.at(Int(2)) == Bytes(b"c")


def test_splitlines() -> None:
    result = Bytes(b"a\nb\nc").splitlines()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_startswith_true() -> None:
    assert Bytes(b"hello").startswith(Bytes(b"hel")) is true


def test_startswith_false() -> None:
    assert Bytes(b"hello").startswith(Bytes(b"xyz")) is false


def test_strip_default() -> None:
    assert Bytes(b"  hello  ").strip() == Bytes(b"hello")


def test_strip_chars() -> None:
    assert Bytes(b"xxhelloxx").strip(Bytes(b"x")) == Bytes(b"hello")


def test_swapcase() -> None:
    assert Bytes(b"Hello World").swapcase() == Bytes(b"hELLO wORLD")


def test_title() -> None:
    assert Bytes(b"hello world").title() == Bytes(b"Hello World")


def test_upper() -> None:
    assert Bytes(b"hello").upper() == Bytes(b"HELLO")


def test_zfill() -> None:
    assert Bytes(b"42").zfill(Int(5)) == Bytes(b"00042")


def test_slice_with_step() -> None:
    assert Bytes(b"abcdef").slice(Int(0), Int(6), Int(2)) == Bytes(b"ace")


def test_contains_non_int_returns_false() -> None:
    assert (Str("a") in Bytes(b"abc")) is False


def test_eq_with_non_bytes_returns_false() -> None:
    assert Bytes(b"x").__eq__(Int(1)) is false


def test_ne_with_non_bytes_returns_true() -> None:
    assert Bytes(b"x").__ne__(Int(1)) is true


def test_add_concatenates() -> None:
    assert Bytes(b"ab") + Bytes(b"cd") == Bytes(b"abcd")


def test_add_accepts_a_byte_array() -> None:
    # CPython concatenates `bytes + bytearray` and answers bytes.
    from poop.types.byte_array import ByteArray

    assert Bytes(b"ab") + ByteArray(bytearray(b"cd")) == Bytes(b"abcd")


def test_add_foreign_operand_is_faithful_not_a_value_leak() -> None:
    with pytest.raises(TypeError) as info:
        _ = Bytes(b"ab") + List(Int(1))
    assert "_value" not in str(info.value)


def test_mul_repeats() -> None:
    assert Bytes(b"ab") * Int(3) == Bytes(b"ababab")


def test_fromhex_parses_hex_string() -> None:
    assert Bytes.fromhex(Str("deadbeef")) == Bytes(bytes.fromhex("deadbeef"))


def test_fromhex_roundtrips_with_hex() -> None:
    b = Bytes(b"\xde\xad\xbe\xef")
    assert Bytes.fromhex(b.hex()) == b


def test_methods_accept_poop_none_kwargs() -> None:
    from poop.types.none import none

    base = Bytes(b"  hi  ")
    assert base.lstrip(chars=none) == Bytes(b"hi  ")
    assert base.rstrip(chars=none) == Bytes(b"  hi")
    assert base.strip(chars=none) == Bytes(b"hi")
    assert base.split(sep=none) == List(Bytes(b"hi"))
    assert base.rsplit(sep=none) == List(Bytes(b"hi"))
    assert Bytes(b"hi").center(Int(6), fillchar=none) == Bytes(b"  hi  ")
    assert Bytes(b"hi").ljust(Int(4), fillchar=none) == Bytes(b"hi  ")
    assert Bytes(b"hi").rjust(Int(4), fillchar=none) == Bytes(b"  hi")
    assert Bytes(b"a\tb").expandtabs(tabsize=none) == Bytes(b"a       b")


def test_count_with_start_and_end() -> None:
    assert Bytes(b"hello hello").count(Bytes(b"hello"), Int(6)) == Int(1)
    assert Bytes(b"hello hello").count(Bytes(b"hello"), Int(0), Int(4)) == Int(0)


def test_find_with_start_and_end() -> None:
    assert Bytes(b"hello hello").find(Bytes(b"hello"), Int(1)) == Int(6)
    assert Bytes(b"hello hello").find(Bytes(b"hello"), Int(0), Int(4)) == Int(-1)


def test_index_with_start_raises_when_absent() -> None:
    import pytest

    with pytest.raises(ValueError):
        Bytes(b"hello hello").index(Bytes(b"hello"), Int(0), Int(4))


def test_index_with_start_finds() -> None:
    assert Bytes(b"hello hello").index(Bytes(b"hello"), Int(1)) == Int(6)


def test_rfind_with_end() -> None:
    assert Bytes(b"hello hello").rfind(Bytes(b"hello"), Int(0), Int(5)) == Int(0)


def test_rindex_with_end() -> None:
    assert Bytes(b"hello hello").rindex(Bytes(b"hello"), Int(0), Int(5)) == Int(0)


def test_rmul_returns_repeated_bytes() -> None:
    assert Bytes(b"ab").__rmul__(Int(3)) == Bytes(b"ababab")


# --- New: optional parameters (proposals 41, 43-44, v1.1.2) ---


def test_split_with_maxsplit() -> None:
    assert Bytes(b"a:b:c:d").split(Bytes(b":"), Int(2)) == List(
        Bytes(b"a"), Bytes(b"b"), Bytes(b"c:d")
    )


def test_rsplit_with_maxsplit() -> None:
    assert Bytes(b"a:b:c:d").rsplit(Bytes(b":"), Int(2)) == List(
        Bytes(b"a:b"), Bytes(b"c"), Bytes(b"d")
    )


def test_startswith_with_start() -> None:
    assert Bytes(b"hello world").startswith(Bytes(b"world"), Int(6)) is true


def test_startswith_with_end_excludes_match() -> None:
    assert Bytes(b"hello world").startswith(Bytes(b"world"), Int(0), Int(5)) is false


def test_endswith_with_start_and_end() -> None:
    assert Bytes(b"hello world").endswith(Bytes(b"hello"), Int(0), Int(5)) is true


def test_replace_with_count() -> None:
    assert Bytes(b"aaa").replace(Bytes(b"a"), Bytes(b"b"), Int(1)) == Bytes(b"baa")


_BAD: Any = List(Int(1), Int(2))


@pytest.mark.parametrize(
    "call, exc",
    [
        pytest.param(lambda: Bytes(b"abc").count(_BAD), TypeError, id="count"),
        pytest.param(lambda: Bytes(b"abc").find(_BAD), TypeError, id="find"),
        pytest.param(lambda: Bytes(b"abc").index(_BAD), TypeError, id="index"),
        pytest.param(lambda: Bytes(b"abc").rfind(_BAD), TypeError, id="rfind"),
        pytest.param(lambda: Bytes(b"abc").rindex(_BAD), TypeError, id="rindex"),
        pytest.param(
            lambda: Bytes(b"abc").replace(_BAD, Bytes(b"x")),
            TypeError,
            id="replace_old",
        ),
        pytest.param(
            lambda: Bytes(b"abc").replace(Bytes(b"a"), _BAD),
            TypeError,
            id="replace_new",
        ),
        pytest.param(lambda: Bytes(b"abc").center(_BAD), TypeError, id="center_width"),
        pytest.param(
            lambda: Bytes(b"abc").center(Int(5), _BAD), TypeError, id="center_fill"
        ),
        pytest.param(lambda: Bytes(b"abc").ljust(_BAD), TypeError, id="ljust"),
        pytest.param(lambda: Bytes(b"abc").rjust(_BAD), TypeError, id="rjust"),
        pytest.param(lambda: Bytes(b"abc").zfill(_BAD), TypeError, id="zfill"),
        pytest.param(lambda: Bytes(b"abc").partition(_BAD), TypeError, id="partition"),
        pytest.param(
            lambda: Bytes(b"abc").rpartition(_BAD), TypeError, id="rpartition"
        ),
        pytest.param(
            lambda: Bytes(b"abc").removeprefix(_BAD), TypeError, id="removeprefix"
        ),
        pytest.param(
            lambda: Bytes(b"abc").removesuffix(_BAD), TypeError, id="removesuffix"
        ),
        pytest.param(
            lambda: Bytes(b"abc").startswith(_BAD), TypeError, id="startswith"
        ),
        pytest.param(lambda: Bytes(b"abc").endswith(_BAD), TypeError, id="endswith"),
        pytest.param(lambda: Bytes(b"abc").strip(_BAD), TypeError, id="strip"),
        pytest.param(lambda: Bytes(b"abc").split(_BAD), TypeError, id="split"),
        pytest.param(lambda: Bytes(b"abc").hex(_BAD), TypeError, id="hex_sep"),
        pytest.param(lambda: Bytes.fromhex(_BAD), TypeError, id="fromhex"),
    ],
)
def test_bytes_wrong_type_arg_is_faithful_not_value_leak(call, exc) -> None:
    # proposals.md item 9: a mandatory argument that carries no `_value` (a
    # List) must reach the underlying Python method raw and raise the faithful
    # exception, never leak the internal `#_value` name through dispatch.
    with pytest.raises(exc) as info:
        call()
    message = str(info.value)
    assert "_value" not in message
    assert "does not understand" not in message


def test_bytes_ordering_against_foreign_raises() -> None:
    import pytest

    from poop.types.bytes import Bytes
    from poop.types.int import Int

    for op in (
        lambda: Bytes(b"a") <= Int(1),
        lambda: Bytes(b"a") > Int(1),
        lambda: Bytes(b"a") >= Int(1),
    ):
        with pytest.raises(TypeError):
            op()


def test_at_accepts_a_boolean_index() -> None:
    assert Bytes(b"ab").at(true) == Int(98)


def test_at_with_a_foreign_index_is_faithful_not_a_value_leak() -> None:
    with pytest.raises(TypeError) as info:
        Bytes(b"ab").at(_BAD)
    assert "_value" not in str(info.value)


def test_reversed_answers_bytes() -> None:
    # `reversed(b"abc")` works in CPython, so `no_reversed` banned a construct
    # this receiver had no substitute for.
    assert Bytes(b"abc").reversed() == Bytes(b"cba")


def test_reversed_of_empty_bytes() -> None:
    assert Bytes(b"").reversed() == Bytes(b"")


# startswith/endswith with a tuple of prefixes — proposal 22


def test_startswith_tuple_of_prefixes() -> None:
    # With `or` banned, a tuple is the only way to ask the question — and the
    # refusal was self-contradicting: the reader *did* pass a tuple, and
    # CPython said a tuple is not a tuple (it meant its own).
    from poop.types.tuple import Tuple

    assert Bytes(b"ab").startswith(Tuple(Bytes(b"a"), Bytes(b"z"))) is true
    assert Bytes(b"ab").startswith(Tuple(Bytes(b"x"), Bytes(b"z"))) is false


def test_endswith_tuple_of_suffixes() -> None:
    from poop.types.tuple import Tuple

    assert Bytes(b"ab").endswith(Tuple(Bytes(b"b"), Bytes(b"z"))) is true
    assert Bytes(b"ab").endswith(Tuple(Bytes(b"x"), Bytes(b"z"))) is false


def test_startswith_empty_tuple_is_false() -> None:
    from poop.types.tuple import Tuple

    assert Bytes(b"ab").startswith(Tuple()) is false


def test_startswith_tuple_with_a_wrong_typed_member_raises() -> None:
    # The members unwrap through `_faithful`, so a `Str` reaches CPython and
    # raises the faithful error instead of being silently coerced.
    from poop.types.string import Str
    from poop.types.tuple import Tuple

    with pytest.raises(TypeError):
        Bytes(b"ab").startswith(Tuple(Str("a")))


def test_sorted_answers_a_list_of_ints() -> None:
    from poop.types.int import Int
    from poop.types.list import List

    assert Bytes(b"ba").sorted() == List(Int(97), Int(98))


def test_ord_answers_the_byte_value() -> None:
    # `no_chr` forbids `ord(x)` and names `x.ord()`; CPython's `ord` takes a
    # one-byte `bytes` (`ord(b"a")` is 97) and only `Str` answered it.
    from poop.types.int import Int

    assert Bytes(b"a").ord() == Int(97)


@pytest.mark.parametrize("data", [b"", b"ab"])
def test_ord_refuses_a_receiver_that_is_not_one_byte(data: bytes) -> None:
    # CPython answers `ord() expected a character, but string of length 2
    # found` — the builtin as a call, and `string` for a receiver that prints
    # as bytes.
    with pytest.raises(TypeError, match="#ord expects a single byte"):
        Bytes(data).ord()


# --- a class-side constructor, under the name a program writes ---
#
# `fromhex` is a classmethod, so `cls` is whatever the program named — and a
# bare builtin name is the alias, whose call is the *converter*. A converter
# takes what a program writes, not the finished Python value a classmethod
# holds, so the only spelling a reader would use was the broken one.


def test_fromhex_under_the_bare_builtin_name() -> None:
    from poop.transformers.bytes import BytesTransformer

    alias = BytesTransformer.BINDINGS["_poop_bytes_cls"]
    assert alias.fromhex(Str("6162")) == Bytes(b"ab")  # ty: ignore[unresolved-attribute]


def test_fromhex_sent_to_an_instance_still_works() -> None:
    assert Bytes(b"").fromhex(Str("6162")) == Bytes(b"ab")


def test_fromhex_on_a_subclass_answers_the_subclass() -> None:
    from poop.transformers.bytes import BytesTransformer

    alias = BytesTransformer.BINDINGS["_poop_bytes_cls"]

    class Sub(alias):  # ty: ignore[invalid-base]
        __slots__ = ()

    made = Sub.fromhex(Str("6162"))
    assert isinstance(made, Sub)
    assert made == Bytes(b"ab")


# Proposal 52. `_needle` was written for the search family and wired into `Str`
# alone, so the same mistake one receiver over answered CPython — and eleven
# more messages on both byte wrappers had no guard at all. None of those
# sentences carries a call, a dunder or an operator, which is why the wording
# sweep ran over about forty sites and passed.
@pytest.mark.parametrize("selector", ["count", "find", "index", "rfind", "rindex"])
def test_the_search_family_refuses_a_str_needle(selector: str) -> None:
    with pytest.raises(TypeError, match=f"#{selector} expects bytes or an int"):
        getattr(Bytes(b"abc"), selector)(Str("a"))


@pytest.mark.parametrize(
    "selector",
    [
        "partition",
        "rpartition",
        "removeprefix",
        "removesuffix",
        "split",
        "rsplit",
        "strip",
        "lstrip",
        "rstrip",
    ],
)
def test_the_bytes_like_family_refuses_a_str_argument(selector: str) -> None:
    with pytest.raises(TypeError, match=f"#{selector} expects bytes"):
        getattr(Bytes(b"abc"), selector)(Str("a"))


def test_join_names_the_message_rather_than_the_sequence_item() -> None:
    # `sequence item 0: expected a bytes-like object, str found` describes a
    # position in a Python sequence, for a message POOP spells `#join`.
    with pytest.raises(TypeError, match="#join expects bytes"):
        Bytes(b"-").join(List(Bytes(b"a"), Str("x")))


def test_replace_refuses_a_str_on_either_side() -> None:
    with pytest.raises(TypeError, match="#replace expects bytes"):
        Bytes(b"abc").replace(Str("a"), Bytes(b"z"))  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match="#replace expects bytes"):
        Bytes(b"abc").replace(Bytes(b"a"), Str("z"))  # ty: ignore[invalid-argument-type]


def test_the_strip_family_still_takes_no_argument() -> None:
    assert Bytes(b"  a  ").strip() == Bytes(b"a")
    assert Bytes(b"xxaxx").strip(Bytes(b"x")) == Bytes(b"a")


def test_a_byte_receiver_still_searches_for_an_integer() -> None:
    # CPython's rule, which the guard must not tighten: `b"ab".count(97)` is 1.
    assert Bytes(b"aab").count(Int(97)) == Int(2)
    assert Bytes(b"aab").includes(Int(97)) is true
