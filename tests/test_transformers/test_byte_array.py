import pytest

from poop.transformers.byte_array import _poop_bytearray_from
from poop.types.byte_array import ByteArray
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List


def test_bytearray_from_list_of_ints() -> None:
    result = _poop_bytearray_from(List(Int(65), Int(66), Int(67)))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray(b"ABC")


def test_bytearray_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert float to bytearray"):
        _poop_bytearray_from(Float(3.14))


def test_bare_bytearray_name_is_rewritten_to_the_mangled_binding() -> None:
    import ast

    from poop.transformers.byte_array import ByteArrayTransformer

    tree = ByteArrayTransformer().transform(ast.parse("f = bytearray"))
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Name)
    assert assign.value.id == "_poop_bytearray"
