import random as _random
from typing import TYPE_CHECKING, Any

from poop.types.float import Float
from poop.types.none import none

if TYPE_CHECKING:
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.object import Object


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

    def uniform(self, a: Float, b: Float) -> Float:
        return Float(self._impl.uniform(a._value, b._value))

    def randint(self, a: Int, b: Int) -> Int:
        from poop.types.int import Int as _Int

        return _Int(self._impl.randint(a._value, b._value))

    def randrange(
        self,
        start: Int,
        stop: Int | None = None,
        step: Int | None = None,
    ) -> Int:
        from poop.types._unwrap import _unwrap
        from poop.types.int import Int as _Int

        stop_value = _unwrap(stop, None)
        step_value = _unwrap(step, 1)
        if stop_value is None:
            return _Int(self._impl.randrange(start._value))
        return _Int(self._impl.randrange(start._value, stop_value, step_value))

    def getrandbits(self, k: Int) -> Int:
        from poop.types.int import Int as _Int

        return _Int(self._impl.getrandbits(k._value))

    def randbytes(self, n: Int) -> Bytes:
        from poop.types.bytes import Bytes as _Bytes

        return _Bytes(self._impl.randbytes(n._value))

    # Collection draws -----------------------------------------------

    def choice(self, seq: Any) -> Object:
        # seq is a POOP iterable; iterate to get a Python list of POOP
        # objects, then delegate to _random.choice.
        return self._impl.choice(list(seq))

    def shuffle(self, x: List) -> NoneClass:
        # In-place mutation of the POOP List's underlying buffer. Mirrors
        # Python's random.shuffle, which mutates and returns None.
        self._impl.shuffle(x._items)
        return none

    def choices(
        self,
        population: Any,
        weights: Any = None,
        *,
        cum_weights: Any = None,
        k: Int | None = None,
    ) -> List:
        from poop.types._unwrap import _unwrap
        from poop.types.list import List as _List

        # Weights flow through random.choices's internal float arithmetic
        # (`cum_weights[-1] + 0.0`), which requires Python numerics — so we
        # unwrap. Population elements stay wrapped because choices just
        # indexes into them and returns them as-is.
        weights_seq = None if weights is None else [w._value for w in weights]
        cum_weights_seq = (
            None if cum_weights is None else [w._value for w in cum_weights]
        )
        k_value = _unwrap(k, 1)
        picks = self._impl.choices(
            list(population),
            weights=weights_seq,
            cum_weights=cum_weights_seq,
            k=k_value,
        )
        return _List(*picks)

    def sample(
        self,
        population: Any,
        k: Int,
        *,
        counts: Any = None,
    ) -> List:
        from poop.types.list import List as _List

        counts_seq = None if counts is None else [c._value for c in counts]
        picks = self._impl.sample(
            list(population),
            k._value,
            counts=counts_seq,
        )
        return _List(*picks)

    # Distributions --------------------------------------------------

    def gauss(self, mu: Float | None = None, sigma: Float | None = None) -> Float:
        from poop.types._unwrap import _unwrap

        return Float(self._impl.gauss(_unwrap(mu, 0.0), _unwrap(sigma, 1.0)))

    def normalvariate(
        self, mu: Float | None = None, sigma: Float | None = None
    ) -> Float:
        from poop.types._unwrap import _unwrap

        return Float(self._impl.normalvariate(_unwrap(mu, 0.0), _unwrap(sigma, 1.0)))

    def lognormvariate(self, mu: Float, sigma: Float) -> Float:
        return Float(self._impl.lognormvariate(mu._value, sigma._value))

    def expovariate(self, lambd: Float | None = None) -> Float:
        from poop.types._unwrap import _unwrap

        return Float(self._impl.expovariate(_unwrap(lambd, 1.0)))

    def gammavariate(self, alpha: Float, beta: Float) -> Float:
        return Float(self._impl.gammavariate(alpha._value, beta._value))

    def betavariate(self, alpha: Float, beta: Float) -> Float:
        return Float(self._impl.betavariate(alpha._value, beta._value))

    def paretovariate(self, alpha: Float) -> Float:
        return Float(self._impl.paretovariate(alpha._value))

    def weibullvariate(self, alpha: Float, beta: Float) -> Float:
        return Float(self._impl.weibullvariate(alpha._value, beta._value))

    def vonmisesvariate(self, mu: Float, kappa: Float) -> Float:
        return Float(self._impl.vonmisesvariate(mu._value, kappa._value))

    def triangular(
        self,
        low: Float | None = None,
        high: Float | None = None,
        mode: Float | None = None,
    ) -> Float:
        from poop.types._unwrap import _unwrap

        return Float(
            self._impl.triangular(
                _unwrap(low, 0.0), _unwrap(high, 1.0), _unwrap(mode, None)
            )
        )

    def binomialvariate(self, n: Int | None = None, p: Float | None = None) -> Int:
        from poop.types._unwrap import _unwrap
        from poop.types.int import Int as _Int

        return _Int(self._impl.binomialvariate(_unwrap(n, 1), _unwrap(p, 0.5)))


_DEFAULT = Random()
