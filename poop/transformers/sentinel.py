from typing import TYPE_CHECKING

from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types._message import article
from poop.types._unwrap import _is_absent
from poop.types.exceptions import MIRRORS
from poop.types.sentinel import Sentinel
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.none import NoneClass


def _poop_sentinel_from(name: object, /, *, repr: object = None) -> Sentinel:
    """`sentinel(name, /, *, repr=None)`, CPython's own signature.

    The keyword is spelt `repr` because that is what a program writes —
    `sentinel("X", repr="<X>")`. The arity shapes (`sentinel()`, a second
    positional) are left to CPython under the cloaked name, as every
    converter's are; the two type refusals are POOP's, where CPython says
    `sentinel() argument 1 must be str, not int` and `argument 'repr' must be
    str or None, not int` — the builtin spelt as a call.
    """
    if not isinstance(name, Str):
        raise MIRRORS["TypeError"](
            f"sentinel's name must be a str, got {article(type(name).__name__)}"
        )
    display: Str | NoneClass | None
    if _is_absent(repr):
        display = None
    elif isinstance(repr, Str):
        display = repr
    else:
        raise MIRRORS["TypeError"](
            f"sentinel's repr must be a str, got {article(type(repr).__name__)}"
        )
    return Sentinel(name, display)


class _SentinelRewriter(BuiltinRewriter):
    builtin = "sentinel"
    call_target = "_poop_sentinel_from"
    name_target = "_poop_sentinel_cls"


class SentinelTransformer(BaseTransformer):
    rewriter = _SentinelRewriter
    BINDINGS = {
        "_poop_sentinel": Sentinel,
        "_poop_sentinel_cls": builtin_alias(Sentinel, _poop_sentinel_from, "sentinel"),
        "_poop_sentinel_from": _poop_sentinel_from,
    }
