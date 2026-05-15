import math as _math
from typing import ClassVar

from poop.types.float import Float
from poop.types.int import Int


class Math:
    """Namespace mirroring Python's `math` module.

    Every public function in `math.*` is exposed as a `@staticmethod`
    with the same name, parameter order, defaults, and return types.
    Constants are recased to UPPER_SNAKE_CASE for consistency with
    `Uuid.NAMESPACE_DNS`, `Secrets.DEFAULT_ENTROPY`, etc.
    """

    PI: ClassVar[Float] = Float(_math.pi)
    E: ClassVar[Float] = Float(_math.e)
    TAU: ClassVar[Float] = Float(_math.tau)
    INF: ClassVar[Float] = Float(_math.inf)
    NAN: ClassVar[Float] = Float(_math.nan)

    # Number theory ------------------------------------------------

    @staticmethod
    def factorial(n: Int) -> Int:
        return Int(_math.factorial(n._value))

    @staticmethod
    def gcd(*integers: Int) -> Int:
        return Int(_math.gcd(*(n._value for n in integers)))

    @staticmethod
    def lcm(*integers: Int) -> Int:
        return Int(_math.lcm(*(n._value for n in integers)))

    @staticmethod
    def comb(n: Int, k: Int) -> Int:
        return Int(_math.comb(n._value, k._value))

    @staticmethod
    def perm(n: Int, k: Int | None = None) -> Int:
        return Int(_math.perm(n._value, k._value if k is not None else None))

    @staticmethod
    def isqrt(n: Int) -> Int:
        return Int(_math.isqrt(n._value))

    # Power & exponential -----------------------------------------

    @staticmethod
    def sqrt(x: Float) -> Float:
        return Float(_math.sqrt(x._value))
