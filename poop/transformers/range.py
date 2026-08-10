from typing import ClassVar

from poop.transformers._forwarding import make_forwarding_rewriter
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.int import Int
from poop.types.range import Range


def _poop_range(
    stop_or_start: Int, stop: Int | None = None, step: Int | None = None
) -> Range:
    if stop is None:
        return Range(Int(0), Int(int(stop_or_start) - 1), Int(1))
    if step is None:
        return Range(Int(int(stop_or_start)), Int(int(stop) - 1), Int(1))
    step_value = int(step)
    sign = 1 if step_value > 0 else -1
    return Range(Int(int(stop_or_start)), Int(int(stop) - sign), Int(step_value))


class RangeTransformer(BaseTransformer):
    rewriter = make_forwarding_rewriter("range", "_poop_range", "_poop_range_cls")
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_range": _poop_range,
        "_poop_range_cls": builtin_alias(Range, _poop_range, "range"),
    }
