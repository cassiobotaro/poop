import binascii as _binascii

import pytest

from poop.interpreter import Interpreter
from poop.types.binascii import Binascii
from poop.types.bytes import Bytes
from poop.types.int import Int

# --- Hex ---


def test_b2a_hex_returns_bytes() -> None:
    result = Binascii.b2a_hex(Bytes(b"\xde\xad"))
    assert isinstance(result, Bytes)
    assert result == Bytes(b"dead")


def test_hexlify_is_alias_of_b2a_hex() -> None:
    data = Bytes(b"abc")
    assert Binascii.hexlify(data) == Binascii.b2a_hex(data)


def test_b2a_hex_with_sep() -> None:
    result = Binascii.b2a_hex(Bytes(b"\xde\xad\xbe\xef"), Bytes(b":"))
    assert result == Bytes(b"de:ad:be:ef")


def test_b2a_hex_with_sep_and_bytes_per_sep() -> None:
    result = Binascii.b2a_hex(Bytes(b"\xde\xad\xbe\xef"), Bytes(b"-"), Int(2))
    assert result == Bytes(b"dead-beef")


def test_a2b_hex_roundtrip() -> None:
    encoded = Binascii.b2a_hex(Bytes(b"\xde\xad"))
    assert Binascii.a2b_hex(encoded) == Bytes(b"\xde\xad")


def test_unhexlify_is_alias_of_a2b_hex() -> None:
    encoded = Bytes(b"deadbeef")
    assert Binascii.unhexlify(encoded) == Binascii.a2b_hex(encoded)


# --- Base64 / qp / uu (lower-level) ---


def test_b2a_base64_returns_bytes_with_newline() -> None:
    result = Binascii.b2a_base64(Bytes(b"abc"))
    assert isinstance(result, Bytes)
    assert result._value.endswith(b"\n")


def test_a2b_base64_roundtrip() -> None:
    encoded = Binascii.b2a_base64(Bytes(b"hello"))
    assert Binascii.a2b_base64(encoded) == Bytes(b"hello")


def test_b2a_qp_returns_bytes() -> None:
    result = Binascii.b2a_qp(Bytes(b"hello"))
    assert isinstance(result, Bytes)


def test_a2b_qp_roundtrip() -> None:
    encoded = Binascii.b2a_qp(Bytes(b"hello world"))
    assert Binascii.a2b_qp(encoded) == Bytes(b"hello world")


def test_b2a_uu_returns_bytes() -> None:
    result = Binascii.b2a_uu(Bytes(b"abc"))
    assert isinstance(result, Bytes)


def test_a2b_uu_roundtrip() -> None:
    encoded = Binascii.b2a_uu(Bytes(b"hello"))
    decoded = Binascii.a2b_uu(encoded)
    assert decoded == Bytes(b"hello")


# --- CRC ---


def test_crc32_with_default_value() -> None:
    result = Binascii.crc32(Bytes(b"hello"))
    assert isinstance(result, Int)
    assert result._value == _binascii.crc32(b"hello")


def test_crc32_with_explicit_value() -> None:
    result = Binascii.crc32(Bytes(b"world"), Int(42))
    assert result._value == _binascii.crc32(b"world", 42)


def test_crc_hqx() -> None:
    result = Binascii.crc_hqx(Bytes(b"hello"), Int(0))
    assert isinstance(result, Int)
    assert result._value == _binascii.crc_hqx(b"hello", 0)


# --- Errors ---


def test_error_is_python_exception_class() -> None:
    assert Binascii.Error is _binascii.Error
    assert issubclass(Binascii.Error, Exception)


def test_incomplete_is_python_exception_class() -> None:
    assert Binascii.Incomplete is _binascii.Incomplete


def test_a2b_hex_raises_error_on_invalid_input() -> None:
    with pytest.raises(Binascii.Error):
        Binascii.a2b_hex(Bytes(b"zz"))


# --- Interpreter integration ---


def test_binascii_reachable_via_interpreter() -> None:
    Interpreter().run_source('binascii.b2a_hex(b"\\xde\\xad").print()')
