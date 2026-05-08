from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.map import Map


class MapTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"Map": Map}
