from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.math import Math


class MathTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"math": Math}
