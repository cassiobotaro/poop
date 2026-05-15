import hashlib as _hashlib
import pathlib as _pathlib

import pytest

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.frozen_set import FrozenSet
from poop.types.hash import Hash, Hashlib
from poop.types.int import Int
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str


def test_hashlib_new_returns_hash_instance() -> None:
    h = Hashlib.new(Str("sha256"), Bytes(b"abc"))
    assert isinstance(h, Hash)


def test_hashlib_new_default_data_is_empty() -> None:
    h = Hashlib.new(Str("sha256"))
    assert h.hexdigest() == Str(_hashlib.sha256(b"").hexdigest())


def test_hashlib_new_matches_python() -> None:
    h = Hashlib.new(Str("sha512"), Bytes(b"hello"))
    assert h.hexdigest() == Str(_hashlib.sha512(b"hello").hexdigest())


def test_hashlib_algorithms_guaranteed_is_frozen_set_of_str() -> None:
    fs = Hashlib.algorithms_guaranteed
    assert isinstance(fs, FrozenSet)
    assert fs.includes(Str("sha256"))


def test_hashlib_algorithms_available_includes_guaranteed() -> None:
    available = Hashlib.algorithms_available
    assert isinstance(available, FrozenSet)
    assert available.includes(Str("sha256"))
    assert available.includes(Str("md5"))


def test_hashlib_hash_class_attribute_points_to_Hash() -> None:
    assert Hashlib.Hash is Hash


def test_hash_update_returns_none() -> None:
    h = Hashlib.new(Str("sha256"))
    assert h.update(Bytes(b"abc")) is none


def test_hash_update_accumulates() -> None:
    incremental = Hashlib.new(Str("sha256"))
    incremental.update(Bytes(b"hel"))
    incremental.update(Bytes(b"lo"))
    one_shot = Hashlib.new(Str("sha256"), Bytes(b"hello"))
    assert incremental.digest() == one_shot.digest()


def test_hash_digest_returns_bytes() -> None:
    h = Hashlib.new(Str("sha256"), Bytes(b"abc"))
    assert isinstance(h.digest(), Bytes)


def test_hash_hexdigest_returns_str() -> None:
    h = Hashlib.new(Str("sha256"), Bytes(b"abc"))
    assert isinstance(h.hexdigest(), Str)


def test_hash_copy_is_independent() -> None:
    h = Hashlib.new(Str("sha256"), Bytes(b"abc"))
    dup = h.copy()
    assert isinstance(dup, Hash)
    assert dup.digest() == h.digest()
    h.update(Bytes(b"xyz"))
    assert dup.digest() != h.digest()


def test_hash_digest_size_property() -> None:
    h = Hashlib.new(Str("sha256"))
    assert isinstance(h.digest_size, Int)
    assert h.digest_size == Int(32)


def test_hash_block_size_property() -> None:
    h = Hashlib.new(Str("sha256"))
    assert isinstance(h.block_size, Int)


def test_hash_name_property() -> None:
    h = Hashlib.new(Str("sha256"))
    assert h.name == Str("sha256")


def test_bytes_md5_shortcut() -> None:
    digest = Bytes(b"abc").md5().hexdigest()
    assert digest == Str(_hashlib.md5(b"abc").hexdigest())  # noqa: S324


def test_bytes_sha1_shortcut() -> None:
    digest = Bytes(b"abc").sha1().hexdigest()
    assert digest == Str(_hashlib.sha1(b"abc").hexdigest())  # noqa: S324


def test_bytes_sha224_shortcut() -> None:
    digest = Bytes(b"abc").sha224().hexdigest()
    assert digest == Str(_hashlib.sha224(b"abc").hexdigest())


def test_bytes_sha256_shortcut() -> None:
    digest = Bytes(b"abc").sha256().hexdigest()
    assert digest == Str(_hashlib.sha256(b"abc").hexdigest())


def test_bytes_sha384_shortcut() -> None:
    digest = Bytes(b"abc").sha384().hexdigest()
    assert digest == Str(_hashlib.sha384(b"abc").hexdigest())


def test_bytes_sha512_shortcut() -> None:
    digest = Bytes(b"abc").sha512().hexdigest()
    assert digest == Str(_hashlib.sha512(b"abc").hexdigest())


def test_bytes_blake2b_shortcut() -> None:
    digest = Bytes(b"abc").blake2b().hexdigest()
    assert digest == Str(_hashlib.blake2b(b"abc").hexdigest())


def test_bytes_blake2s_shortcut() -> None:
    digest = Bytes(b"abc").blake2s().hexdigest()
    assert digest == Str(_hashlib.blake2s(b"abc").hexdigest())


def test_bytes_sha3_256_shortcut() -> None:
    digest = Bytes(b"abc").sha3_256().hexdigest()
    assert digest == Str(_hashlib.sha3_256(b"abc").hexdigest())


def test_bytes_sha3_512_shortcut() -> None:
    digest = Bytes(b"abc").sha3_512().hexdigest()
    assert digest == Str(_hashlib.sha3_512(b"abc").hexdigest())


def test_bytes_shake_128_requires_length() -> None:
    digest = Bytes(b"abc").shake_128().hexdigest(Int(16))
    assert digest == Str(_hashlib.shake_128(b"abc").hexdigest(16))


def test_bytes_shake_256_requires_length() -> None:
    digest = Bytes(b"abc").shake_256().digest(Int(32))
    assert digest == Bytes(_hashlib.shake_256(b"abc").digest(32))


def test_bytes_pbkdf2_hmac_default_dklen() -> None:
    derived = Bytes(b"password").pbkdf2_hmac(Str("sha256"), Bytes(b"salt"), Int(10_000))
    expected = _hashlib.pbkdf2_hmac("sha256", b"password", b"salt", 10_000)
    assert derived == Bytes(expected)


def test_bytes_pbkdf2_hmac_with_dklen() -> None:
    derived = Bytes(b"password").pbkdf2_hmac(
        Str("sha256"), Bytes(b"salt"), Int(10_000), Int(16)
    )
    assert derived.len() == Int(16)


def test_bytes_scrypt_default_dklen() -> None:
    derived = Bytes(b"password").scrypt(
        salt=Bytes(b"salt"), n=Int(2), r=Int(8), p=Int(1)
    )
    expected = _hashlib.scrypt(
        b"password", salt=b"salt", n=2, r=8, p=1, maxmem=0, dklen=64
    )
    assert derived == Bytes(expected)


def test_bytes_scrypt_with_dklen() -> None:
    derived = Bytes(b"password").scrypt(
        salt=Bytes(b"salt"), n=Int(2), r=Int(8), p=Int(1), dklen=Int(32)
    )
    assert derived.len() == Int(32)


def test_hashlib_file_digest(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "blob.bin"
    target.write_bytes(b"hello world")
    digest = Hashlib.file_digest(Path(Str(str(target))), Str("sha256"))
    assert isinstance(digest, Hash)
    assert digest.hexdigest() == Str(_hashlib.sha256(b"hello world").hexdigest())


def test_hash_new_unknown_algorithm_raises() -> None:
    with pytest.raises(ValueError):
        Hashlib.new(Str("not-a-real-algo"))


def test_hashlib_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["hashlib"] is Hashlib
    assert DEFAULT_NAMESPACE["Hash"] is Hash


def test_hashlib_reachable_via_interpreter() -> None:
    Interpreter().run_source('b"abc".sha256().hexdigest().print()')


def test_hash_reachable_via_interpreter() -> None:
    Interpreter().run_source('hashlib.new("sha256", b"abc").hexdigest().print()')
