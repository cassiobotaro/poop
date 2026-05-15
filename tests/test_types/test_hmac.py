import hmac as _hmac

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.bytes import Bytes
from poop.types.hmac import HMAC, Hmac
from poop.types.int import Int
from poop.types.none import none
from poop.types.string import Str


def test_new_returns_hmac_instance() -> None:
    h = Hmac.new(Bytes(b"secret"), Bytes(b"hello"))
    assert isinstance(h, HMAC)


def test_new_default_digestmod_is_sha256() -> None:
    h = Hmac.new(Bytes(b"secret"))
    assert h.name == Str("hmac-sha256")


def test_new_with_explicit_digestmod() -> None:
    h = Hmac.new(Bytes(b"secret"), Bytes(b"hello"), Str("sha1"))
    assert h.name == Str("hmac-sha1")


def test_hexdigest_returns_poop_str() -> None:
    h = Hmac.new(Bytes(b"key"), Bytes(b"msg"))
    result = h.hexdigest()
    assert isinstance(result, Str)
    # Compare to underlying hmac.
    expected = _hmac.new(b"key", b"msg", "sha256").hexdigest()
    assert result == Str(expected)


def test_digest_returns_poop_bytes() -> None:
    h = Hmac.new(Bytes(b"key"), Bytes(b"msg"))
    assert isinstance(h.digest(), Bytes)


def test_update_returns_none() -> None:
    h = Hmac.new(Bytes(b"key"))
    result = h.update(Bytes(b"more"))
    assert result is none


def test_update_changes_digest() -> None:
    h1 = Hmac.new(Bytes(b"key"))
    h1.update(Bytes(b"hello"))
    h2 = Hmac.new(Bytes(b"key"), Bytes(b"hello"))
    assert h1.digest() == h2.digest()


def test_copy_returns_independent_hmac() -> None:
    h = Hmac.new(Bytes(b"key"), Bytes(b"abc"))
    dup = h.copy()
    assert isinstance(dup, HMAC)
    assert dup.digest() == h.digest()
    # Mutating one doesn't affect the other.
    h.update(Bytes(b"xyz"))
    assert dup.digest() != h.digest()


def test_digest_size() -> None:
    h = Hmac.new(Bytes(b"key"))
    assert isinstance(h.digest_size, Int)
    assert h.digest_size._value == 32  # sha256


def test_block_size() -> None:
    h = Hmac.new(Bytes(b"key"))
    assert isinstance(h.block_size, Int)


def test_digest_one_shot_function() -> None:
    result = Hmac.digest(Bytes(b"key"), Bytes(b"msg"), Str("sha256"))
    assert isinstance(result, Bytes)
    expected = _hmac.digest(b"key", b"msg", "sha256")
    assert result == Bytes(expected)


def test_compare_digest_equal_returns_true() -> None:
    result = Hmac.compare_digest(Str("abc"), Str("abc"))
    assert isinstance(result, Boolean)
    assert result is true


def test_compare_digest_unequal_returns_false() -> None:
    assert Hmac.compare_digest(Str("abc"), Str("xyz")) is false


def test_compare_digest_bytes() -> None:
    assert Hmac.compare_digest(Bytes(b"k"), Bytes(b"k")) is true


def test_hmac_reachable_via_interpreter() -> None:
    Interpreter().run_source('hmac.new(b"k", b"m").hexdigest().print()')


def test_HMAC_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["HMAC"] is HMAC
