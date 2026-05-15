from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.random import _DEFAULT, Random


class RandomTransformer(BaseTransformer):
    # Two bindings, mirroring Python's distinction between the
    # `random` module and the `Random` class:
    #   `random` (lowercase) → singleton instance acting as the
    #            module-level API: random.random(), random.choice(xs), ...
    #   `Random` (PascalCase) → the class itself, callable as a
    #            constructor: r = Random(seed)
    BINDINGS: ClassVar[dict[str, object]] = {
        "random": _DEFAULT,
        "Random": Random,
    }
