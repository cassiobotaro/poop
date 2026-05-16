import pytest

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.codecs import CodecInfo, Codecs
from poop.types.int import Int
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- BOM constants ---


def test_bom_utf8_value() -> None:
    assert isinstance(Codecs.BOM_UTF8, Bytes)
    assert Codecs.BOM_UTF8._value == b"\xef\xbb\xbf"


def test_bom_utf16_le_value() -> None:
    assert Codecs.BOM_UTF16_LE._value == b"\xff\xfe"


def test_bom_utf16_be_value() -> None:
    assert Codecs.BOM_UTF16_BE._value == b"\xfe\xff"


def test_bom_utf32_le_value() -> None:
    assert Codecs.BOM_UTF32_LE._value == b"\xff\xfe\x00\x00"


def test_bom_utf32_be_value() -> None:
    assert Codecs.BOM_UTF32_BE._value == b"\x00\x00\xfe\xff"


def test_bom_aliases_match() -> None:
    # `BOM` aliases the platform-native UTF-16 BOM in CPython.
    assert isinstance(Codecs.BOM, Bytes)
    assert isinstance(Codecs.BOM_LE, Bytes)
    assert isinstance(Codecs.BOM_BE, Bytes)


# --- encode / decode ---


def test_encode_default_utf8() -> None:
    result = Codecs.encode(Str("hello"))
    assert isinstance(result, Bytes)
    assert result._value == b"hello"


def test_encode_latin1() -> None:
    result = Codecs.encode(Str("café"), Str("latin-1"))
    assert isinstance(result, Bytes)
    assert result._value == b"caf\xe9"


def test_encode_rot13_returns_str() -> None:
    # rot_13 is a str-to-str codec.
    result = Codecs.encode(Str("hello"), Str("rot_13"))
    assert isinstance(result, Str)
    assert result._value == "uryyb"


def test_encode_hex_codec_returns_bytes() -> None:
    # hex_codec is bytes-to-bytes.
    result = Codecs.encode(Bytes(b"\x00\xff"), Str("hex_codec"))
    assert isinstance(result, Bytes)
    assert result._value == b"00ff"


def test_decode_default_utf8() -> None:
    result = Codecs.decode(Bytes(b"hello"))
    assert isinstance(result, Str)
    assert result == Str("hello")


def test_decode_hex_codec() -> None:
    result = Codecs.decode(Bytes(b"00ff"), Str("hex_codec"))
    assert isinstance(result, Bytes)
    assert result._value == b"\x00\xff"


def test_decode_errors_replace() -> None:
    raw = Bytes(b"\xc3\x28")  # invalid UTF-8 sequence
    result = Codecs.decode(raw, Str("utf-8"), errors=Str("replace"))
    assert isinstance(result, Str)
    assert "�" in result._value


def test_encode_rejects_non_poop() -> None:
    with pytest.raises(TypeError):
        Codecs.encode(Int(42))  # ty: ignore[invalid-argument-type]


# --- lookup ---


def test_lookup_returns_codec_info() -> None:
    info = Codecs.lookup(Str("utf-8"))
    assert isinstance(info, CodecInfo)


def test_codec_info_name_is_str() -> None:
    info = Codecs.lookup(Str("UTF-8"))
    assert info.name == Str("utf-8")


def test_codec_info_encode_returns_tuple() -> None:
    info = Codecs.lookup(Str("utf-8"))
    result = info.encode(Str("abc"))
    assert isinstance(result, Tuple)
    encoded = result.at(Int(0))
    length = result.at(Int(1))
    assert isinstance(encoded, Bytes)
    assert encoded._value == b"abc"
    assert length == Int(3)


def test_codec_info_decode_returns_tuple() -> None:
    info = Codecs.lookup(Str("utf-8"))
    result = info.decode(Bytes(b"abc"))
    assert isinstance(result, Tuple)
    decoded = result.at(Int(0))
    assert isinstance(decoded, Str)
    assert decoded == Str("abc")


def test_codec_info_incremental_classes() -> None:
    info = Codecs.lookup(Str("utf-8"))
    assert info.incrementalencoder is not None
    assert info.incrementaldecoder is not None


def test_codec_info_repr_includes_name() -> None:
    info = Codecs.lookup(Str("utf-8"))
    assert "utf-8" in str(info)


def test_lookup_unknown_raises() -> None:
    with pytest.raises(LookupError):
        Codecs.lookup(Str("not_a_real_codec_xyz"))


# --- Interpreter integration ---


def test_codecs_encode_reachable_via_interpreter() -> None:
    Interpreter().run_source('codecs.encode("hello").print()')


def test_codecs_decode_reachable_via_interpreter() -> None:
    Interpreter().run_source('codecs.decode(b"hello").print()')


def test_codecs_lookup_reachable_via_interpreter() -> None:
    Interpreter().run_source('codecs.lookup("utf-8").name.print()')


def test_codecs_bom_constant_reachable_via_interpreter() -> None:
    Interpreter().run_source("codecs.BOM_UTF8.len().print()")
