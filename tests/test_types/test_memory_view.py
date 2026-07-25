import pytest

from poop.parser import parse
from poop.transformers.byte_array import ByteArrayTransformer, _poop_bytearray_from
from poop.transformers.bytes import BytesTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.memory_view import MemoryViewTransformer, _poop_memoryview_from
from poop.types.boolean import false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.memory_view import MemoryView
from poop.types.string import Str


def _mv(data: bytes) -> MemoryView:
    return MemoryView(memoryview(data))


def test_len() -> None:
    assert _mv(b"hello").len() == Int(5)


def test_empty_len() -> None:
    assert _mv(b"").len() == Int(0)


def test_dunder_len() -> None:
    assert len(_mv(b"abc")) == 3


def test_at_returns_byte_as_int() -> None:
    mv = _mv(b"ABC")
    assert mv.at(Int(0)) == Int(65)
    assert mv.at(Int(1)) == Int(66)


def test_at_returns_byte_value() -> None:
    assert _mv(b"Z").at(Int(0)) == Int(90)


def test_do_yields_int_values() -> None:
    seen: list[Int] = []
    _mv(b"\x01\x02\x03").do(lambda b: seen.append(b))
    assert seen == [Int(1), Int(2), Int(3)]


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    result = _mv(b"\x01\x02").map(lambda b: b)
    assert isinstance(result, Map)


def test_map_transforms() -> None:
    result = List(*_mv(b"\x01\x02").map(lambda b: Int(b._value * 10)))
    assert result.at(Int(0)) == Int(10)
    assert result.at(Int(1)) == Int(20)


def test_iter_yields_int_values() -> None:
    items = list(_mv(b"\x0a\x0b"))
    assert items == [Int(10), Int(11)]


def test_tobytes() -> None:
    assert _mv(b"hi").tobytes() == Bytes(b"hi")


def test_tobytes_with_order() -> None:
    assert _mv(b"hi").tobytes(Str("C")) == Bytes(b"hi")


def test_eq_equal() -> None:
    assert _mv(b"abc") == _mv(b"abc")


def test_eq_different() -> None:
    assert (_mv(b"abc") == _mv(b"xyz")) is false


def test_ne_different() -> None:
    assert (_mv(b"abc") != _mv(b"xyz")) is true


def test_str_representation() -> None:
    result = str(_mv(b"hi"))
    assert result.startswith("<memory at")


def test_repr_equals_str() -> None:
    mv = _mv(b"test")
    assert repr(mv) == str(mv)


def test_transformer_from_bytes() -> None:
    tree = parse('mv = memoryview(b"abc")')
    tree = BytesTransformer().transform(tree)
    tree = MemoryViewTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_bytes": Bytes,
        "_poop_memoryview_from": _poop_memoryview_from,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["mv"]
    assert isinstance(result, MemoryView)
    assert result.len() == Int(3)


def test_transformer_from_bytearray() -> None:
    tree = parse("mv = memoryview(bytearray(3))")
    tree = IntTransformer().transform(tree)
    tree = ByteArrayTransformer().transform(tree)
    tree = MemoryViewTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_int": Int,
        "_poop_bytearray_from": _poop_bytearray_from,
        "_poop_memoryview_from": _poop_memoryview_from,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["mv"]
    assert isinstance(result, MemoryView)
    assert result.len() == Int(3)


def test_factory_from_bytes_object() -> None:
    mv = _poop_memoryview_from(Bytes(b"hello"))
    assert isinstance(mv, MemoryView)
    assert mv.len() == Int(5)


def test_factory_from_bytearray_object() -> None:
    mv = _poop_memoryview_from(ByteArray(bytearray(b"hi")))
    assert isinstance(mv, MemoryView)
    assert mv.len() == Int(2)


def test_factory_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="bytes-like object is required"):
        _poop_memoryview_from(Int(5))


def test_eq_with_bytes_compares_by_value() -> None:
    # CPython: memoryview(b"abc") == b"abc" is True.
    assert _mv(b"abc") == Bytes(b"abc")
    assert (_mv(b"abc") == Bytes(b"xyz")) is false


def test_eq_with_bytearray_compares_by_value() -> None:
    assert _mv(b"abc") == ByteArray(bytearray(b"abc"))


def test_hash_matches_equal_bytes() -> None:
    # eq/hash invariant: equal-by-value across the "bytes" group must hash equal.
    assert hash(_mv(b"abc")) == hash(Bytes(b"abc"))


def test_eq_with_non_memory_view_returns_false() -> None:
    assert _mv(b"abc").__eq__(Int(1)) is false


def test_ne_with_non_memory_view_returns_true() -> None:
    assert _mv(b"abc").__ne__(Int(1)) is true


def test_bare_memoryview_name_is_rewritten() -> None:
    import ast

    tree = MemoryViewTransformer().transform(ast.parse("f = memoryview"))
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Name)
    assert assign.value.id == "_poop_memoryview"


def test_at_accepts_a_boolean_index() -> None:
    assert MemoryView(memoryview(b"ab")).at(true) == Int(98)
