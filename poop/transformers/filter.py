from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.filter import Filter


class FilterTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"Filter": Filter}
