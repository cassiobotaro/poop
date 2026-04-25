from poop.transformers.byte_array import _poop_bytearray_from
from poop.types.byte_array import ByteArray
from poop.types.int import Int


def test_bytearray_from_list_of_ints() -> None:
    from poop.types.list import List

    result = _poop_bytearray_from(List(Int(65), Int(66), Int(67)))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray(b"ABC")


def test_bytearray_from_unsupported_type_returns_empty() -> None:
    from poop.types.float import Float

    result = _poop_bytearray_from(Float(3.14))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray()
