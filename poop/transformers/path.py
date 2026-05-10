from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.path import Path


class PathTransformer(BaseTransformer):
    BINDINGS: ClassVar[dict[str, object]] = {"Path": Path}
