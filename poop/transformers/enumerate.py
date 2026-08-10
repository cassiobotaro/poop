from typing import ClassVar

from poop.transformers._forwarding import make_forwarding_rewriter
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.enumerate import Enumerate
from poop.types.int import Int


def _poop_enumerate(source: object, start: Int | None = None) -> Enumerate:
    return Enumerate(source, start)


class EnumerateTransformer(BaseTransformer):
    rewriter = make_forwarding_rewriter(
        "enumerate", "_poop_enumerate", "_poop_enumerate_cls"
    )
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_enumerate_cls": builtin_alias(Enumerate, _poop_enumerate, "enumerate"),
    }
