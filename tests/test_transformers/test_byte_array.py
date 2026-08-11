import pytest

from poop.transformers.byte_array import _poop_bytearray_from
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def test_bytearray_from_list_of_ints() -> None:
    result = _poop_bytearray_from(List(Int(65), Int(66), Int(67)))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray(b"ABC")


def test_bytearray_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert float to bytearray"):
        _poop_bytearray_from(Float(3.14))


def test_bytearray_builds_from_text_with_an_encoding() -> None:
    # `Bytes` and `ByteArray` mirror each other message for message, and this
    # was the one half-pair: `bytearray("ab", "utf-8")` — legal Python — was
    # refused as an over-supplied constructor.
    result = _poop_bytearray_from(Str("ab"), Str("utf-8"))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray(b"ab")


def test_bytearray_from_text_without_an_encoding_says_so() -> None:
    # It used to fall through the `Iterable` branch to `bytearray(<str
    # chars>)`, answering `'str' object cannot be interpreted as an integer` —
    # a message about integers, for an argument that is text.
    with pytest.raises(TypeError, match="string argument without an encoding"):
        _poop_bytearray_from(Str("ab"))


def test_bytearray_routes_the_encoding_through_the_codec_surface() -> None:
    with pytest.raises(ValueError, match="unknown encoding 'rot13'"):
        _poop_bytearray_from(Str("ab"), Str("rot13"))
    with pytest.raises(ValueError, match="ascii cannot encode 'é' at position 0"):
        _poop_bytearray_from(Str("é"), Str("ascii"))


def test_bytearray_refuses_an_encoding_without_text() -> None:
    with pytest.raises(TypeError, match="encoding without a string argument"):
        _poop_bytearray_from(Bytes(b"ab"), Str("utf-8"))


def test_bytearray_from_text_takes_the_errors_handler_too() -> None:
    result = _poop_bytearray_from(Str("aéb"), Str("ascii"), Str("ignore"))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray(b"ab")


def test_bare_bytearray_name_is_rewritten_to_the_mangled_binding() -> None:
    import ast

    from poop.transformers.byte_array import ByteArrayTransformer

    tree = ByteArrayTransformer().transform(ast.parse("f = bytearray"))
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Name)
    assert assign.value.id == "_poop_bytearray_cls"
