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
