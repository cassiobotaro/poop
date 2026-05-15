from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.random import _DEFAULT


class RandomTransformer(BaseTransformer):
    # `Random` in DEFAULT_NAMESPACE is the singleton *instance*, not the
    # class. Its methods serve both as the namespace (Random.random()) and
    # as the entry point for fresh seeded instances (Random.new(seed)).
    BINDINGS: ClassVar[dict[str, object]] = {"Random": _DEFAULT}
