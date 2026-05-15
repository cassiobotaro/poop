import uuid as _uuid

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.uuid import UUID, Uuid

# --- Construction ---


def test_construct_from_hex_string() -> None:
    u = UUID(Str("12345678-1234-5678-1234-567812345678"))
    assert isinstance(u, UUID)
    assert str(u._impl) == "12345678-1234-5678-1234-567812345678"


def test_construct_from_hex_keyword() -> None:
    u = UUID(hex=Str("12345678-1234-5678-1234-567812345678"))
    assert str(u._impl) == "12345678-1234-5678-1234-567812345678"


def test_construct_from_bytes() -> None:
    raw = b"\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78"
    u = UUID(bytes=Bytes(raw))
    assert u._impl.bytes == raw


def test_construct_from_int() -> None:
    u = UUID(int=Int(0))
    assert u._impl.int == 0


# --- Representations ---


def test_hex_returns_poop_str() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.hex, Str)
    assert len(u.hex._value) == 32


def test_urn_returns_poop_str() -> None:
    u = Uuid.uuid4()
    assert u.urn._value.startswith("urn:uuid:")


def test_int_returns_poop_int() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.int, Int)


def test_bytes_returns_poop_bytes() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.bytes, Bytes)
    assert len(u.bytes._value) == 16


def test_bytes_le_returns_poop_bytes() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.bytes_le, Bytes)


def test_fields_returns_tuple_of_ints() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.fields, Tuple)
    assert u.fields.len()._value == 6


# --- Field accessors ---


def test_time_low_is_int() -> None:
    assert isinstance(Uuid.uuid4().time_low, Int)


def test_version_4() -> None:
    u = Uuid.uuid4()
    assert u.version == Int(4)


def test_variant_rfc4122() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.variant, Str)


def test_is_safe_is_lowercase_str() -> None:
    u = Uuid.uuid4()
    assert isinstance(u.is_safe, Str)
    assert u.is_safe._value in ("safe", "unsafe", "unknown")


# --- Generators ---


def test_uuid1_returns_uuid() -> None:
    u = Uuid.uuid1()
    assert isinstance(u, UUID)
    assert u.version == Int(1)


def test_uuid3_with_namespace_dns() -> None:
    u = Uuid.uuid3(Uuid.NAMESPACE_DNS, Str("example.com"))
    assert u.version == Int(3)


def test_uuid4_is_random() -> None:
    a = Uuid.uuid4()
    b = Uuid.uuid4()
    assert a != b


def test_uuid5_with_namespace_url() -> None:
    u = Uuid.uuid5(Uuid.NAMESPACE_URL, Str("https://example.com"))
    assert u.version == Int(5)


def test_uuid6_returns_uuid() -> None:
    u = Uuid.uuid6()
    assert u.version == Int(6)


def test_uuid7_returns_uuid() -> None:
    u = Uuid.uuid7()
    assert u.version == Int(7)


def test_uuid8_returns_uuid() -> None:
    u = Uuid.uuid8()
    assert u.version == Int(8)


def test_getnode_returns_poop_int() -> None:
    assert isinstance(Uuid.getnode(), Int)


# --- Constants ---


def test_namespace_dns_is_uuid() -> None:
    assert isinstance(Uuid.NAMESPACE_DNS, UUID)
    assert Uuid.NAMESPACE_DNS._impl == _uuid.NAMESPACE_DNS


def test_namespace_url_is_uuid() -> None:
    assert isinstance(Uuid.NAMESPACE_URL, UUID)


def test_namespace_oid_is_uuid() -> None:
    assert isinstance(Uuid.NAMESPACE_OID, UUID)


def test_namespace_x500_is_uuid() -> None:
    assert isinstance(Uuid.NAMESPACE_X500, UUID)


def test_nil_is_all_zeros() -> None:
    assert isinstance(Uuid.NIL, UUID)
    assert Uuid.NIL.int == Int(0)


def test_max_is_all_ones() -> None:
    assert isinstance(Uuid.MAX, UUID)
    assert Uuid.MAX.int._value == (1 << 128) - 1


def test_variant_constants_are_str() -> None:
    assert isinstance(Uuid.RFC_4122, Str)
    assert isinstance(Uuid.RESERVED_NCS, Str)
    assert isinstance(Uuid.RESERVED_MICROSOFT, Str)
    assert isinstance(Uuid.RESERVED_FUTURE, Str)


# --- Equality ---


def test_equal_uuids() -> None:
    a = UUID(Str("12345678-1234-5678-1234-567812345678"))
    b = UUID(Str("12345678-1234-5678-1234-567812345678"))
    assert a == b


def test_unequal_uuids() -> None:
    assert Uuid.uuid4() != Uuid.uuid4()


# --- Interpreter integration ---


def test_uuid_namespace_reachable_via_interpreter() -> None:
    Interpreter().run_source("uuid.uuid4().hex.print()")


def test_UUID_class_reachable_via_interpreter() -> None:
    Interpreter().run_source('UUID("12345678-1234-5678-1234-567812345678").hex.print()')
