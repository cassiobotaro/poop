from typing import Any

import pytest

from poop.parser import parse
from poop.transformers.byte_array import ByteArrayTransformer, _poop_bytearray_from
from poop.transformers.bytes import BytesTransformer
from poop.transformers.int import IntTransformer
from poop.types.boolean import false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_empty_bytearray() -> None:
    assert ByteArray().len() == Int(0)


def test_from_bytearray_value() -> None:
    ba = ByteArray(bytearray(b"abc"))
    assert ba.len() == Int(3)


def test_init_from_bytearray_does_not_alias_input() -> None:
    raw = bytearray(b"abc")
    ba = ByteArray(raw)
    raw[0] = ord("Z")
    assert ba.at(Int(0)) == Int(ord("a"))


def test_init_from_byte_array_does_not_alias_source() -> None:
    src = ByteArray(bytearray(b"abc"))
    copy = ByteArray(src)
    src.at_put(Int(0), Int(ord("Z")))
    assert copy.at(Int(0)) == Int(ord("a"))


def test_len() -> None:
    assert ByteArray(bytearray(b"hello")).len() == Int(5)


def test_dunder_len() -> None:
    assert len(ByteArray(bytearray(b"hi"))) == 2


def test_at_returns_byte_value_as_int() -> None:
    ba = ByteArray(bytearray(b"ABC"))
    assert ba.at(Int(0)) == Int(65)
    assert ba.at(Int(1)) == Int(66)


def test_at_zero_indexed() -> None:
    assert ByteArray(bytearray(b"Z")).at(Int(0)) == Int(90)


def test_at_put_mutates() -> None:
    ba = ByteArray(bytearray(b"abc"))
    ba.at_put(Int(0), Int(90))  # 'Z' = 90
    assert ba.at(Int(0)) == Int(90)


def test_at_put_returns_self() -> None:
    ba = ByteArray(bytearray(b"abc"))
    result = ba.at_put(Int(0), Int(65))
    assert result is ba


def test_includes_true() -> None:
    assert ByteArray(bytearray(b"hello")).includes(Int(104)) is true  # ord('h') == 104


def test_includes_false() -> None:
    assert ByteArray(bytearray(b"hello")).includes(Int(0)) is false


def test_includes_non_value_argument_raises_faithful_typeerror() -> None:
    # A non-`_value` argument (List) must reach bytearray.__contains__ raw and
    # raise the faithful TypeError, not leak the internal `_value` name.
    ba = ByteArray(bytearray(b"hi"))
    with pytest.raises(TypeError, match="bytes-like object"):
        ba.includes(List(Int(1)))  # ty: ignore[invalid-argument-type]


def test_contains_dunder() -> None:
    ba = ByteArray(bytearray(b"abc"))
    assert Int(97) in ba  # ord('a')
    assert Int(0) not in ba


def test_decode_utf8() -> None:
    assert ByteArray(bytearray(b"hello")).decode(Str("utf-8")) == Str("hello")


def test_decode_ascii() -> None:
    assert ByteArray(bytearray(b"hi")).decode(Str("ascii")) == Str("hi")


def test_hex() -> None:
    result = ByteArray(bytearray(b"\xff\x00")).hex()
    assert isinstance(result, Str)
    assert result == Str("ff00")


def test_do_yields_int_byte_values() -> None:
    seen: list[Int] = []
    ByteArray(bytearray(b"\x01\x02\x03")).do(lambda b: seen.append(b))
    assert seen == [Int(1), Int(2), Int(3)]


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    result = ByteArray(bytearray(b"\x01\x02")).map(lambda b: b)
    assert isinstance(result, Map)


def test_map_transforms_bytes() -> None:
    result = List(*ByteArray(bytearray(b"\x01\x02")).map(lambda b: Int(b._value * 2)))
    assert result.at(Int(0)) == Int(2)
    assert result.at(Int(1)) == Int(4)


def test_iter_yields_int_byte_values() -> None:
    items = list(ByteArray(bytearray(b"\x0a\x0b")))
    assert items == [Int(10), Int(11)]


def test_eq_equal() -> None:
    assert ByteArray(bytearray(b"abc")) == ByteArray(bytearray(b"abc"))


def test_eq_different() -> None:
    assert (ByteArray(bytearray(b"abc")) == ByteArray(bytearray(b"xyz"))) is false


def test_ne_different() -> None:
    assert (ByteArray(bytearray(b"abc")) != ByteArray(bytearray(b"xyz"))) is true


def test_not_hashable() -> None:
    with pytest.raises(TypeError):
        hash(ByteArray(bytearray(b"hello")))  # type: ignore[call-overload]


def test_str_representation() -> None:
    assert str(ByteArray(bytearray(b"hi"))) == "bytearray(b'hi')"


def test_repr_equals_str() -> None:
    ba = ByteArray(bytearray(b"test"))
    assert repr(ba) == str(ba)


def test_transformer_no_args() -> None:
    tree = parse("ba = bytearray()")
    tree = ByteArrayTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_bytearray_from": _poop_bytearray_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["ba"]
    assert isinstance(result, ByteArray)
    assert result.len() == Int(0)


def test_transformer_from_bytes_arg() -> None:
    tree = parse('ba = bytearray(b"abc")')
    tree = BytesTransformer().transform(tree)
    tree = ByteArrayTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_bytes": Bytes,
        "_poop_bytearray_from": _poop_bytearray_from,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["ba"]
    assert isinstance(result, ByteArray)
    assert result.len() == Int(3)


def test_transformer_from_int_arg() -> None:
    tree = parse("ba = bytearray(5)")
    tree = IntTransformer().transform(tree)
    tree = ByteArrayTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_int": Int,
        "_poop_bytearray_from": _poop_bytearray_from,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["ba"]
    assert isinstance(result, ByteArray)
    assert result.len() == Int(5)


def test_bytearray_mutable_via_at_put() -> None:
    ba = ByteArray(bytearray(3))  # [0, 0, 0]
    ba.at_put(Int(1), Int(42))
    assert ba.at(Int(1)) == Int(42)


def test_append_adds_byte() -> None:
    ba = ByteArray()
    ba.append(Int(65))
    assert ba.len() == Int(1)
    assert ba.at(Int(0)) == Int(65)


def test_append_returns_none() -> None:
    ba = ByteArray()
    assert ba.append(Int(1)) is none


def test_clear_empties() -> None:
    ba = ByteArray(bytearray(b"hello"))
    ba.clear()
    assert ba.len() == Int(0)


def test_clear_returns_none() -> None:
    ba = ByteArray(bytearray(b"hi"))
    assert ba.clear() is none


def test_copy_returns_new_bytearray() -> None:
    ba = ByteArray(bytearray(b"hi"))
    c = ba.copy()
    assert c is not ba
    assert c == ba


def test_copy_is_shallow() -> None:
    ba = ByteArray(bytearray(b"hi"))
    c = ba.copy()
    ba.clear()
    assert c.len() == Int(2)


def test_extend_mutates() -> None:
    ba = ByteArray(bytearray(b"ab"))
    ba.extend(ByteArray(bytearray(b"cd")))
    assert ba.len() == Int(4)


def test_extend_returns_none() -> None:
    ba = ByteArray()
    assert ba.extend(ByteArray(bytearray(b"x"))) is none


def test_insert_adds_at_position() -> None:
    ba = ByteArray(bytearray(b"ac"))
    ba.insert(Int(1), Int(98))  # ord('b') == 98
    assert ba.at(Int(1)) == Int(98)
    assert ba.len() == Int(3)


def test_insert_returns_none() -> None:
    ba = ByteArray(bytearray(b"a"))
    assert ba.insert(Int(0), Int(65)) is none


def test_pop_last() -> None:
    ba = ByteArray(bytearray(b"ab"))
    val = ba.pop()
    assert val == Int(98)  # ord('b')
    assert ba.len() == Int(1)


def test_pop_at_index() -> None:
    ba = ByteArray(bytearray(b"abc"))
    val = ba.pop(Int(0))
    assert val == Int(97)  # ord('a')
    assert ba.len() == Int(2)


def test_remove_first_occurrence() -> None:
    ba = ByteArray(bytearray(b"abab"))
    ba.remove(Int(97))  # ord('a')
    assert ba.len() == Int(3)
    assert ba.at(Int(0)) == Int(98)


def test_remove_returns_none() -> None:
    ba = ByteArray(bytearray(b"a"))
    assert ba.remove(Int(97)) is none


def test_reverse_mutates() -> None:
    ba = ByteArray(bytearray(b"abc"))
    ba.reverse()
    assert ba.at(Int(0)) == Int(99)  # ord('c')
    assert ba.at(Int(2)) == Int(97)  # ord('a')


def test_reverse_returns_none() -> None:
    ba = ByteArray(bytearray(b"hi"))
    assert ba.reverse() is none


def test_capitalize() -> None:
    assert ByteArray(bytearray(b"hello world")).capitalize() == ByteArray(
        bytearray(b"Hello world")
    )


def test_center_no_fill() -> None:
    assert ByteArray(bytearray(b"hi")).center(Int(6)) == ByteArray(bytearray(b"  hi  "))


def test_count() -> None:
    assert ByteArray(bytearray(b"abcabc")).count(ByteArray(bytearray(b"ab"))) == Int(2)


def test_endswith_true() -> None:
    assert ByteArray(bytearray(b"hello")).endswith(ByteArray(bytearray(b"lo"))) is true


def test_endswith_false() -> None:
    assert ByteArray(bytearray(b"hello")).endswith(ByteArray(bytearray(b"hi"))) is false


def test_expandtabs_default() -> None:
    assert ByteArray(bytearray(b"a\tb")).expandtabs() == ByteArray(
        bytearray(b"a       b")
    )


def test_find_found() -> None:
    assert ByteArray(bytearray(b"hello")).find(ByteArray(bytearray(b"ll"))) == Int(2)


def test_find_not_found() -> None:
    assert ByteArray(bytearray(b"hello")).find(ByteArray(bytearray(b"xyz"))) == Int(-1)


def test_index_found() -> None:
    assert ByteArray(bytearray(b"hello")).index(ByteArray(bytearray(b"ll"))) == Int(2)


def test_isalnum_true() -> None:
    assert ByteArray(bytearray(b"abc123")).isalnum() is true


def test_isalpha_true() -> None:
    assert ByteArray(bytearray(b"abc")).isalpha() is true


def test_isascii_true() -> None:
    assert ByteArray(bytearray(b"hello")).isascii() is true


def test_isdigit_true() -> None:
    assert ByteArray(bytearray(b"123")).isdigit() is true


def test_islower_true() -> None:
    assert ByteArray(bytearray(b"hello")).islower() is true


def test_isspace_true() -> None:
    assert ByteArray(bytearray(b"   ")).isspace() is true


def test_istitle_true() -> None:
    assert ByteArray(bytearray(b"Hello World")).istitle() is true


def test_isupper_true() -> None:
    assert ByteArray(bytearray(b"HELLO")).isupper() is true


def test_join() -> None:
    sep = ByteArray(bytearray(b"-"))
    parts = List(ByteArray(bytearray(b"a")), ByteArray(bytearray(b"b")))
    assert sep.join(parts) == ByteArray(bytearray(b"a-b"))


def test_join_accepts_other_bytes_like() -> None:
    sep = ByteArray(bytearray(b"-"))
    parts = List(Bytes(b"a"), ByteArray(bytearray(b"b")))
    assert sep.join(parts) == ByteArray(bytearray(b"a-b"))


def test_join_non_bytes_like_raises() -> None:
    # CPython raises TypeError rather than silently dropping the int element.
    sep = ByteArray(bytearray(b"-"))
    parts = List(ByteArray(bytearray(b"a")), Int(5))
    with pytest.raises(TypeError, match="bytes-like object"):
        sep.join(parts)


def test_ljust() -> None:
    assert ByteArray(bytearray(b"hi")).ljust(Int(5)) == ByteArray(bytearray(b"hi   "))


def test_lower() -> None:
    assert ByteArray(bytearray(b"HELLO")).lower() == ByteArray(bytearray(b"hello"))


def test_lstrip_default() -> None:
    assert ByteArray(bytearray(b"  hello")).lstrip() == ByteArray(bytearray(b"hello"))


def test_partition() -> None:
    result = ByteArray(bytearray(b"hello world")).partition(ByteArray(bytearray(b" ")))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == ByteArray(bytearray(b"hello"))
    assert result.at(Int(2)) == ByteArray(bytearray(b"world"))


def test_removeprefix() -> None:
    assert ByteArray(bytearray(b"hello")).removeprefix(
        ByteArray(bytearray(b"hel"))
    ) == ByteArray(bytearray(b"lo"))


def test_removesuffix() -> None:
    assert ByteArray(bytearray(b"hello")).removesuffix(
        ByteArray(bytearray(b"lo"))
    ) == ByteArray(bytearray(b"hel"))


def test_replace() -> None:
    assert ByteArray(bytearray(b"aabb")).replace(
        ByteArray(bytearray(b"aa")), ByteArray(bytearray(b"XX"))
    ) == ByteArray(bytearray(b"XXbb"))


def test_rfind() -> None:
    assert ByteArray(bytearray(b"abcabc")).rfind(ByteArray(bytearray(b"ab"))) == Int(3)


def test_rindex() -> None:
    assert ByteArray(bytearray(b"abcabc")).rindex(ByteArray(bytearray(b"ab"))) == Int(3)


def test_rjust() -> None:
    assert ByteArray(bytearray(b"hi")).rjust(Int(5)) == ByteArray(bytearray(b"   hi"))


def test_rpartition() -> None:
    result = ByteArray(bytearray(b"hello world")).rpartition(ByteArray(bytearray(b" ")))
    assert isinstance(result, Tuple)
    assert result.at(Int(2)) == ByteArray(bytearray(b"world"))


def test_rsplit() -> None:
    result = ByteArray(bytearray(b"a b c")).rsplit()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_rstrip_default() -> None:
    assert ByteArray(bytearray(b"hello  ")).rstrip() == ByteArray(bytearray(b"hello"))


def test_split_no_sep() -> None:
    result = ByteArray(bytearray(b"a b c")).split()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_split_with_sep() -> None:
    result = ByteArray(bytearray(b"a,b,c")).split(ByteArray(bytearray(b",")))
    assert isinstance(result, List)
    assert result.at(Int(0)) == ByteArray(bytearray(b"a"))


def test_splitlines() -> None:
    result = ByteArray(bytearray(b"a\nb\nc")).splitlines()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_startswith_true() -> None:
    assert (
        ByteArray(bytearray(b"hello")).startswith(ByteArray(bytearray(b"hel"))) is true
    )


def test_startswith_false() -> None:
    assert (
        ByteArray(bytearray(b"hello")).startswith(ByteArray(bytearray(b"xyz"))) is false
    )


def test_strip_default() -> None:
    assert ByteArray(bytearray(b"  hello  ")).strip() == ByteArray(bytearray(b"hello"))


def test_swapcase() -> None:
    assert ByteArray(bytearray(b"Hello")).swapcase() == ByteArray(bytearray(b"hELLO"))


def test_title() -> None:
    assert ByteArray(bytearray(b"hello world")).title() == ByteArray(
        bytearray(b"Hello World")
    )


def test_upper() -> None:
    assert ByteArray(bytearray(b"hello")).upper() == ByteArray(bytearray(b"HELLO"))


def test_zfill() -> None:
    assert ByteArray(bytearray(b"42")).zfill(Int(5)) == ByteArray(bytearray(b"00042"))


def test_slice_with_step() -> None:
    ba = ByteArray(bytearray(b"abcdef"))
    assert ba.slice(Int(0), Int(6), Int(2)) == ByteArray(bytearray(b"ace"))


def test_contains_non_int_returns_false() -> None:
    assert (Str("a") in ByteArray(bytearray(b"abc"))) is False


def test_eq_with_non_byte_array_returns_false() -> None:
    assert ByteArray(bytearray(b"x")).__eq__(Int(1)) is false


def test_ne_with_non_byte_array_returns_true() -> None:
    assert ByteArray(bytearray(b"x")).__ne__(Int(1)) is true


def test_add_concatenates() -> None:
    a = ByteArray(bytearray(b"ab"))
    b = ByteArray(bytearray(b"cd"))
    assert a + b == ByteArray(bytearray(b"abcd"))


def test_mul_repeats() -> None:
    assert ByteArray(bytearray(b"ab")) * Int(3) == ByteArray(bytearray(b"ababab"))


def test_mul_by_boolean_folds_to_int() -> None:
    # bool is an int subclass in CPython: bytearray(b"ab") * True == b"ab".
    assert ByteArray(bytearray(b"ab")) * true == ByteArray(bytearray(b"ab"))
    assert ByteArray(bytearray(b"ab")) * false == ByteArray(bytearray())


def test_center_with_fillchar() -> None:
    ba = ByteArray(bytearray(b"hi"))
    fill = ByteArray(bytearray(b"*"))
    assert ba.center(Int(6), fill) == ByteArray(bytearray(b"**hi**"))


def test_ljust_with_fillchar() -> None:
    ba = ByteArray(bytearray(b"hi"))
    fill = ByteArray(bytearray(b"*"))
    assert ba.ljust(Int(5), fill) == ByteArray(bytearray(b"hi***"))


def test_lstrip_with_chars() -> None:
    ba = ByteArray(bytearray(b"xxxhi"))
    chars = ByteArray(bytearray(b"x"))
    assert ba.lstrip(chars) == ByteArray(bytearray(b"hi"))


def test_rjust_with_fillchar() -> None:
    ba = ByteArray(bytearray(b"hi"))
    fill = ByteArray(bytearray(b"*"))
    assert ba.rjust(Int(5), fill) == ByteArray(bytearray(b"***hi"))


def test_rstrip_with_chars() -> None:
    ba = ByteArray(bytearray(b"hixxx"))
    chars = ByteArray(bytearray(b"x"))
    assert ba.rstrip(chars) == ByteArray(bytearray(b"hi"))


def test_strip_with_chars() -> None:
    ba = ByteArray(bytearray(b"xxhixx"))
    chars = ByteArray(bytearray(b"x"))
    assert ba.strip(chars) == ByteArray(bytearray(b"hi"))


def test_expandtabs_with_tabsize() -> None:
    ba = ByteArray(bytearray(b"a\tb"))
    assert ba.expandtabs(Int(4)) == ByteArray(bytearray(b"a   b"))


def test_methods_accept_poop_none_kwargs() -> None:
    from poop.types.none import none

    base = ByteArray(bytearray(b"  hi  "))
    assert base.lstrip(chars=none) == ByteArray(bytearray(b"hi  "))
    assert base.rstrip(chars=none) == ByteArray(bytearray(b"  hi"))
    assert base.strip(chars=none) == ByteArray(bytearray(b"hi"))
    assert base.split(sep=none) == List(ByteArray(bytearray(b"hi")))
    assert base.rsplit(sep=none) == List(ByteArray(bytearray(b"hi")))
    assert ByteArray(bytearray(b"hi")).center(Int(6), fillchar=none) == ByteArray(
        bytearray(b"  hi  ")
    )
    assert ByteArray(bytearray(b"hi")).ljust(Int(4), fillchar=none) == ByteArray(
        bytearray(b"hi  ")
    )
    assert ByteArray(bytearray(b"hi")).rjust(Int(4), fillchar=none) == ByteArray(
        bytearray(b"  hi")
    )
    assert ByteArray(bytearray(b"a\tb")).expandtabs(tabsize=none) == ByteArray(
        bytearray(b"a       b")
    )


def test_rmul_returns_repeated_bytearray() -> None:
    assert ByteArray(bytearray(b"ab")).__rmul__(Int(3)) == ByteArray(
        bytearray(b"ababab")
    )


def test_rmul_by_boolean_folds_to_int() -> None:
    assert true * ByteArray(bytearray(b"ab")) == ByteArray(bytearray(b"ab"))


# --- New: optional parameters (proposals 41-44, v1.1.2) ---


def test_split_with_maxsplit() -> None:
    assert ByteArray(bytearray(b"a:b:c:d")).split(
        ByteArray(bytearray(b":")), Int(2)
    ) == List(
        ByteArray(bytearray(b"a")),
        ByteArray(bytearray(b"b")),
        ByteArray(bytearray(b"c:d")),
    )


def test_rsplit_with_maxsplit() -> None:
    assert ByteArray(bytearray(b"a:b:c:d")).rsplit(
        ByteArray(bytearray(b":")), Int(2)
    ) == List(
        ByteArray(bytearray(b"a:b")),
        ByteArray(bytearray(b"c")),
        ByteArray(bytearray(b"d")),
    )


def test_count_with_start_and_end() -> None:
    ba = ByteArray(bytearray(b"hello hello hello"))
    sub = ByteArray(bytearray(b"hello"))
    assert ba.count(sub, Int(6)) == Int(2)
    assert ba.count(sub, Int(6), Int(11)) == Int(1)


def test_find_with_start() -> None:
    ba = ByteArray(bytearray(b"hello hello"))
    sub = ByteArray(bytearray(b"hello"))
    assert ba.find(sub, Int(1)) == Int(6)


def test_index_with_start_raises_when_absent() -> None:
    import pytest

    ba = ByteArray(bytearray(b"hello hello"))
    sub = ByteArray(bytearray(b"hello"))
    with pytest.raises(ValueError):
        ba.index(sub, Int(0), Int(4))


def test_rfind_with_end() -> None:
    ba = ByteArray(bytearray(b"hello hello"))
    sub = ByteArray(bytearray(b"hello"))
    assert ba.rfind(sub, Int(0), Int(5)) == Int(0)


def test_rindex_with_start() -> None:
    ba = ByteArray(bytearray(b"hello hello"))
    sub = ByteArray(bytearray(b"hello"))
    assert ba.rindex(sub, Int(0), Int(5)) == Int(0)


def test_startswith_with_start() -> None:
    ba = ByteArray(bytearray(b"hello world"))
    assert ba.startswith(ByteArray(bytearray(b"world")), Int(6)) is true


def test_endswith_with_end() -> None:
    ba = ByteArray(bytearray(b"hello world"))
    assert ba.endswith(ByteArray(bytearray(b"hello")), Int(0), Int(5)) is true


def test_replace_with_count() -> None:
    ba = ByteArray(bytearray(b"aaa"))
    assert ba.replace(
        ByteArray(bytearray(b"a")), ByteArray(bytearray(b"b")), Int(1)
    ) == ByteArray(bytearray(b"baa"))


def test_eq_bytes_and_bytearray_equal_by_value() -> None:
    # CPython: b"ab" == bytearray(b"ab") is True (both directions).
    assert ByteArray(bytearray(b"ab")) == Bytes(b"ab")
    assert Bytes(b"ab") == ByteArray(bytearray(b"ab"))


def test_eq_bytes_and_bytearray_different_values() -> None:
    assert (ByteArray(bytearray(b"ab")) == Bytes(b"xy")) is false
    assert (ByteArray(bytearray(b"ab")) != Bytes(b"xy")) is true


_BAD: Any = List(Int(1), Int(2))


@pytest.mark.parametrize(
    "call, exc",
    [
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).count(_BAD), TypeError, id="count"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).find(_BAD), TypeError, id="find"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).index(_BAD), TypeError, id="index"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).rfind(_BAD), TypeError, id="rfind"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).rindex(_BAD), TypeError, id="rindex"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).replace(
                _BAD, ByteArray(bytearray(b"x"))
            ),
            TypeError,
            id="replace_old",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).replace(
                ByteArray(bytearray(b"a")), _BAD
            ),
            TypeError,
            id="replace_new",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).center(_BAD),
            TypeError,
            id="center_width",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).ljust(_BAD), TypeError, id="ljust"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).rjust(_BAD), TypeError, id="rjust"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).zfill(_BAD), TypeError, id="zfill"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).partition(_BAD),
            TypeError,
            id="partition",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).rpartition(_BAD),
            TypeError,
            id="rpartition",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).removeprefix(_BAD),
            TypeError,
            id="removeprefix",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).removesuffix(_BAD),
            TypeError,
            id="removesuffix",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).startswith(_BAD),
            TypeError,
            id="startswith",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).endswith(_BAD),
            TypeError,
            id="endswith",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).strip(_BAD), TypeError, id="strip"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).split(_BAD), TypeError, id="split"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).hex(_BAD), TypeError, id="hex_sep"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).append(_BAD), TypeError, id="append"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).extend(_BAD), TypeError, id="extend"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).insert(_BAD, Int(5)),
            TypeError,
            id="insert",
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).remove(_BAD), TypeError, id="remove"
        ),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).pop(_BAD), TypeError, id="pop"
        ),
        pytest.param(lambda: ByteArray(bytearray(b"abc")).at(_BAD), TypeError, id="at"),
        pytest.param(
            lambda: ByteArray(bytearray(b"abc")).at_put(_BAD, Int(5)),
            TypeError,
            id="at_put",
        ),
    ],
)
def test_byte_array_wrong_type_arg_is_faithful_not_value_leak(call, exc) -> None:
    # proposals.md item 9: a mandatory argument that carries no `_value` (a
    # List) must reach the underlying Python method raw and raise the faithful
    # exception, never leak the internal `#_value` name through dispatch.
    with pytest.raises(exc) as info:
        call()
    message = str(info.value)
    assert "_value" not in message
    assert "does not understand" not in message


def test_bytearray_ordering_between_bytearrays() -> None:
    from poop.types.boolean import false, true
    from poop.types.byte_array import ByteArray

    assert (ByteArray(b"abc") < ByteArray(b"abd")) is true
    assert (ByteArray(b"abc") <= ByteArray(b"abc")) is true
    assert (ByteArray(b"abd") > ByteArray(b"abc")) is true
    assert (ByteArray(b"abc") >= ByteArray(b"abc")) is true
    assert (ByteArray(b"abd") < ByteArray(b"abc")) is false


def test_bytearray_ordering_against_foreign_raises() -> None:
    import pytest

    from poop.types.byte_array import ByteArray
    from poop.types.int import Int

    for op in (
        lambda: ByteArray(b"a") < Int(1),
        lambda: ByteArray(b"a") <= Int(1),
        lambda: ByteArray(b"a") > Int(1),
        lambda: ByteArray(b"a") >= Int(1),
    ):
        with pytest.raises(TypeError):
            op()
