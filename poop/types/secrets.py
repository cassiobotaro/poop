import secrets as _secrets
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._unwrap import _unwrap
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.object import Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Secrets:
    """Namespace mirroring Python's `secrets` module.

    Cryptographically-secure draws and comparisons. Non-secure
    randomness belongs to `random`, not here — POOP deliberately
    separates the two to match Python's API split.

    `secrets.SystemRandom` is intentionally not surfaced — its
    instance API duplicates the module-level functions exposed here.
    """

    DEFAULT_ENTROPY: ClassVar[Int] = Int(_secrets.DEFAULT_ENTROPY)

    # Token minting ----------------------------------------------------

    @staticmethod
    def token_bytes(nbytes: Int | None = None) -> Bytes:
        return Bytes(_secrets.token_bytes(_unwrap(nbytes, None)))

    @staticmethod
    def token_hex(nbytes: Int | None = None) -> Str:
        return Str(_secrets.token_hex(_unwrap(nbytes, None)))

    @staticmethod
    def token_urlsafe(nbytes: Int | None = None) -> Str:
        return Str(_secrets.token_urlsafe(_unwrap(nbytes, None)))

    # Secure draws -----------------------------------------------------

    @staticmethod
    def choice(seq: Any) -> Object:
        # seq is a POOP iterable; iterate to get a Python list of POOP
        # objects, then delegate to secrets.choice.
        return _secrets.choice(list(seq))

    @staticmethod
    def randbelow(exclusive_upper_bound: Int) -> Int:
        return Int(_secrets.randbelow(exclusive_upper_bound._value))

    @staticmethod
    def randbits(k: Int) -> Int:
        return Int(_secrets.randbits(k._value))

    # Constant-time comparison ----------------------------------------

    @staticmethod
    def compare_digest(a: Str | Bytes, b: Str | Bytes, /) -> Boolean:
        return true if _secrets.compare_digest(a._value, b._value) else false
