from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers._forwarding import make_forwarding_rewriter
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.enumerate import Enumerate
from poop.types.exceptions import MIRRORS

if TYPE_CHECKING:
    from poop.types.int import Int


def _poop_enumerate(*args: object, **kwargs: object) -> Enumerate:
    refuse_extra_arguments(
        "enumerate",
        args,
        kwargs,
        most=2,
        built_from="a collection and an optional start",
        hint="write enumerate(collection, start)",
    )
    if not args:
        raise MIRRORS["TypeError"](
            "enumerate is built from a collection and an optional start, got "
            "nothing — write enumerate(collection, start)"
        )
    return Enumerate(args[0], cast("Int | None", args[1] if len(args) > 1 else None))


class EnumerateTransformer(BaseTransformer):
    rewriter = make_forwarding_rewriter(
        "enumerate", "_poop_enumerate", "_poop_enumerate_cls"
    )
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_enumerate_cls": builtin_alias(Enumerate, _poop_enumerate, "enumerate"),
    }
