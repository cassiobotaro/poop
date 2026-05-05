from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.slice import Slice


class SliceTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"Slice": Slice}
