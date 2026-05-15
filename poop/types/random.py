import random as _random
from typing import TYPE_CHECKING

from poop.types.float import Float
from poop.types.none import none

if TYPE_CHECKING:
    from poop.types.int import Int
    from poop.types.none import NoneClass


class Random:
    """Wraps `random.Random` mirroring Python's module-level interface.

    The class itself is hidden from POOP source: `poop/transformers/random.py`
    exposes a module-level singleton (`_DEFAULT`) under the name `Random` in
    `DEFAULT_NAMESPACE`. The singleton acts as the namespace
    (`Random.random()` is the singleton's instance method); `Random.new(seed)`
    is a factory on the singleton returning a fresh, independently-seeded
    `Random` instance.

    This mirrors how Python's `random` module works: `random.random` is
    literally `_inst.random`, a bound method on a module-level singleton.

    Cryptographic draws belong to `Secrets`, not here.
    """

    def __init__(self, seed: Int | None = None) -> None:
        from poop.types._unwrap import _unwrap

        # noqa: S311 -- non-cryptographic by design; use Secrets for crypto.
        self._impl = _random.Random(_unwrap(seed, None))  # noqa: S311

    def new(self, seed: Int | None = None) -> Random:
        return Random(seed)

    # Bookkeeping ----------------------------------------------------

    def seed(self, a: Int | None = None, version: Int | None = None) -> NoneClass:
        from poop.types._unwrap import _unwrap

        self._impl.seed(_unwrap(a, None), version=_unwrap(version, 2))
        return none

    # Core draws -----------------------------------------------------

    def random(self) -> Float:
        return Float(self._impl.random())


_DEFAULT = Random()
