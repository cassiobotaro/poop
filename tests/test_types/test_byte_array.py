from poop.types.boolean import false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def test_empty_bytearray() -> None:
    assert ByteArray().len() == Int(0)


def test_from_bytearray_value() -> None:
    ba = ByteArray(bytearray(b"abc"))
    assert ba.len() == Int(3)


def test_len() -> None:
    assert ByteArray(bytearray(b"hello")).len() == Int(5)


def test_dunder_len() -> None:
    assert len(ByteArray(bytearray(b"hi"))) == 2


def test_at_returns_byte_value_as_int() -> None:
    ba = ByteArray(bytearray(b"ABC"))
    assert ba.at(Int(0)) == Int(65)
    assert ba.at(Int(1)) == Int(66)


def test_getitem_dunder() -> None:
    assert ByteArray(bytearray(b"Z"))[Int(0)] == Int(90)


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
    ByteArray(bytearray(b"\x01\x02\x03")).do(lambda b: seen.append(b))  # type: ignore[arg-type]
    assert seen == [Int(1), Int(2), Int(3)]


def test_map_returns_list() -> None:
    result = ByteArray(bytearray(b"\x01\x02")).map(lambda b: b)
    assert isinstance(result, List)


def test_map_transforms_bytes() -> None:
    result = ByteArray(bytearray(b"\x01\x02")).map(lambda b: Int(b._value * 2))  # type: ignore[attr-defined]
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
    import pytest

    with pytest.raises(TypeError):
        hash(ByteArray(bytearray(b"hello")))  # type: ignore[call-overload]


def test_str_representation() -> None:
    assert str(ByteArray(bytearray(b"hi"))) == "bytearray(b'hi')"


def test_repr_equals_str() -> None:
    ba = ByteArray(bytearray(b"test"))
    assert repr(ba) == str(ba)


def test_transformer_no_args() -> None:
    from poop.parser import parse
    from poop.transformers.byte_array import ByteArrayTransformer, _poop_bytearray_from

    tree = parse("ba = bytearray()")
    tree = ByteArrayTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_bytearray_from": _poop_bytearray_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["ba"]
    assert isinstance(result, ByteArray)
    assert result.len() == Int(0)


def test_transformer_from_bytes_arg() -> None:
    from poop.parser import parse
    from poop.transformers.byte_array import ByteArrayTransformer, _poop_bytearray_from
    from poop.transformers.bytes import BytesTransformer

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
    from poop.parser import parse
    from poop.transformers.byte_array import ByteArrayTransformer, _poop_bytearray_from
    from poop.transformers.int import IntTransformer

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
