import secrets as _secrets

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.secrets import Secrets
from poop.types.string import Str


def test_default_entropy_constant() -> None:
    assert isinstance(Secrets.DEFAULT_ENTROPY, Int)
    assert Secrets.DEFAULT_ENTROPY._value == _secrets.DEFAULT_ENTROPY
    assert Secrets.DEFAULT_ENTROPY._value == 32


def test_token_bytes_returns_poop_bytes_with_default_length() -> None:
    result = Secrets.token_bytes()
    assert isinstance(result, Bytes)
    assert len(result._value) == _secrets.DEFAULT_ENTROPY


def test_token_bytes_honors_nbytes() -> None:
    result = Secrets.token_bytes(Int(16))
    assert isinstance(result, Bytes)
    assert len(result._value) == 16


def test_token_hex_returns_poop_str() -> None:
    result = Secrets.token_hex(Int(8))
    assert isinstance(result, Str)
    assert len(result._value) == 16  # 8 bytes → 16 hex chars
    int(result._value, 16)  # parses as hex


def test_token_urlsafe_returns_poop_str() -> None:
    result = Secrets.token_urlsafe(Int(8))
    assert isinstance(result, Str)
    # URL-safe alphabet only.
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
    assert set(result._value).issubset(allowed)


def test_randbelow_returns_poop_int_in_range() -> None:
    for _ in range(20):
        result = Secrets.randbelow(Int(10))
        assert isinstance(result, Int)
        assert 0 <= result._value < 10


def test_randbits_returns_poop_int_within_bits() -> None:
    for _ in range(20):
        result = Secrets.randbits(Int(4))
        assert isinstance(result, Int)
        assert 0 <= result._value < 16


def test_choice_picks_element_from_list() -> None:
    items = List(Str("a"), Str("b"), Str("c"))
    picked = Secrets.choice(items)
    assert picked in (Str("a"), Str("b"), Str("c"))


def test_compare_digest_equal_strings_returns_true() -> None:
    result = Secrets.compare_digest(Str("hunter2"), Str("hunter2"))
    assert isinstance(result, Boolean)
    assert result is true


def test_compare_digest_unequal_strings_returns_false() -> None:
    result = Secrets.compare_digest(Str("hunter2"), Str("password"))
    assert result is false


def test_compare_digest_bytes() -> None:
    result = Secrets.compare_digest(Bytes(b"abc"), Bytes(b"abc"))
    assert result is true


def test_secrets_reachable_via_interpreter() -> None:
    Interpreter().run_source("secrets.token_hex(8).print()")


def test_secrets_default_entropy_reachable_via_interpreter() -> None:
    Interpreter().run_source("secrets.DEFAULT_ENTROPY.print()")
