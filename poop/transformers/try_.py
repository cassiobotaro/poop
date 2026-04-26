from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.try_ import Try


class TryTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"Try": Try}
