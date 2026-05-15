import math as _math
from typing import ClassVar

from poop.types.float import Float


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

    @staticmethod
    def sqrt(x: Float) -> Float:
        return Float(_math.sqrt(x._value))
