from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def test_empty_bytes() -> None:
    assert Bytes(b"").len() == Int(0)


def test_len() -> None:
    assert Bytes(b"abc").len() == Int(3)


def test_dunder_len() -> None:
    assert len(Bytes(b"hi")) == 2


def test_at_returns_byte_value_as_int() -> None:
    assert Bytes(b"ABC").at(Int(0)) == Int(65)
    assert Bytes(b"ABC").at(Int(1)) == Int(66)


def test_getitem_dunder() -> None:
    assert Bytes(b"Z")[Int(0)] == Int(90)


def test_includes_true() -> None:
    assert Bytes(b"hello").includes(Int(104)) is true  # ord('h') == 104


def test_includes_false() -> None:
    assert Bytes(b"hello").includes(Int(0)) is false


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
    Bytes(b"\x01\x02\x03").do(lambda b: seen.append(b))  # type: ignore[arg-type]
    assert seen == [Int(1), Int(2), Int(3)]


def test_map_returns_list() -> None:
    result = Bytes(b"\x01\x02").map(lambda b: b)
    assert isinstance(result, List)


def test_map_transforms_bytes() -> None:
    result = Bytes(b"\x01\x02").map(lambda b: Int(b._value * 2))  # type: ignore[attr-defined]
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


def test_hashable() -> None:
    assert isinstance(hash(Bytes(b"hello")), int)


def test_equal_bytes_have_equal_hash() -> None:
    assert hash(Bytes(b"abc")) == hash(Bytes(b"abc"))


def test_bytes_can_be_dict_key() -> None:
    from poop.types.dict import Dict

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
    from poop.parser import parse
    from poop.transformers.bytes import BytesTransformer

    tree = parse('b = b"hello"')
    tree = BytesTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_bytes": Bytes}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["b"]
    assert isinstance(result, Bytes)
    assert result.len() == Int(5)


def test_transformer_empty_literal() -> None:
    from poop.parser import parse
    from poop.transformers.bytes import BytesTransformer

    tree = parse("b = b''")
    tree = BytesTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_bytes": Bytes}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["b"], Bytes)
    assert ns["b"].len() == Int(0)  # type: ignore[union-attr]


def test_transformer_does_not_affect_str_literals() -> None:
    from poop.parser import parse
    from poop.transformers.bytes import BytesTransformer

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
    from poop.types.list import List

    parts = List(Bytes(b"a"), Bytes(b"b"), Bytes(b"c"))
    assert Bytes(b"-").join(parts) == Bytes(b"a-b-c")


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
    from poop.types.tuple import Tuple

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
    from poop.types.tuple import Tuple

    result = Bytes(b"hello world").rpartition(Bytes(b" "))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Bytes(b"hello")
    assert result.at(Int(2)) == Bytes(b"world")


def test_rsplit_no_sep() -> None:
    from poop.types.list import List

    result = Bytes(b"a b c").rsplit()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_rsplit_with_sep() -> None:
    from poop.types.list import List

    result = Bytes(b"a,b,c").rsplit(Bytes(b","))
    assert isinstance(result, List)
    assert result.at(Int(0)) == Bytes(b"a")


def test_rstrip_default() -> None:
    assert Bytes(b"hello  ").rstrip() == Bytes(b"hello")


def test_rstrip_chars() -> None:
    assert Bytes(b"helloxx").rstrip(Bytes(b"x")) == Bytes(b"hello")


def test_split_no_sep() -> None:
    from poop.types.list import List

    result = Bytes(b"a b c").split()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_split_with_sep() -> None:
    from poop.types.list import List

    result = Bytes(b"a,b,c").split(Bytes(b","))
    assert isinstance(result, List)
    assert result.at(Int(0)) == Bytes(b"a")
    assert result.at(Int(2)) == Bytes(b"c")


def test_splitlines() -> None:
    from poop.types.list import List

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
