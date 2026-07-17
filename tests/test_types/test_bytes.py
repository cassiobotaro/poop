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


def test_includes_non_value_argument_raises_faithful_typeerror() -> None:
    # A non-`_value` argument (List) must reach bytes.__contains__ raw and raise
    # the faithful TypeError, not leak the internal `_value` name through
    # dispatch. Mirrors CPython's `[1] in b"hello"`.
    with pytest.raises(TypeError, match="bytes-like object"):
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
    with pytest.raises(TypeError, match="bytes-like object"):
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
        pytest.param(lambda: Bytes(b"abc").hex(_BAD), ValueError, id="hex_sep"),
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
