from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.with_ import With


class WithTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"With": With}
