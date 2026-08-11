from operator import index as _index
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers._forwarding import make_forwarding_rewriter
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.range import Range

if TYPE_CHECKING:
    from poop.types._index import Index


def _poop_range(*args: object, **kwargs: object) -> Range:
    """`range(stop)` / `range(start, stop[, step])`, read by index.

    `_index`, not `int`: `Range.__init__` already takes the index rung of the
    tower for this reason, and the converter in front of it read `int(...)`
    instead — which *truncates* where `index` refuses, so `range(3.5)` answered
    `range(0, 3)` and `range(1, 10, 2.0)` a step of 2, silently running over a
    different sequence than the program describes. It also refused the
    non-numeric cases in `int`'s vocabulary (`int() argument must be a string,
    a bytes-like object or a real number`), naming a call for something the
    program spelt `range`. `index` answers `'float' object cannot be
    interpreted as an integer`, which is CPython's own and, through the cloak,
    names the wrapper by the builtin it stands for. The boolean rung still
    passes, since admitting it is exactly what `index` is for.
    """
    refuse_extra_arguments(
        "range",
        args,
        kwargs,
        most=3,
        built_from="a stop, or a start and a stop and an optional step",
        hint="write range(stop) or range(start, stop, step)",
    )
    if not args:
        raise MIRRORS["TypeError"](
            "range is built from a stop, or a start and a stop and an optional "
            "step, got nothing — write range(stop) or range(start, stop, step)"
        )
    # `*args: object` is what the guard above needs to count; `_index` refuses
    # anything outside the index rung at runtime, which is the check that
    # matters and the one this converter exists for.
    stop_or_start = cast("Index", args[0])
    stop = cast("Index | None", args[1] if len(args) > 1 else None)
    step = cast("Index | None", args[2] if len(args) > 2 else None)
    if stop is None:
        return Range(Int(0), Int(_index(stop_or_start) - 1), Int(1))
    if step is None:
        return Range(Int(_index(stop_or_start)), Int(_index(stop) - 1), Int(1))
    step_value = _index(step)
    sign = 1 if step_value > 0 else -1
    return Range(Int(_index(stop_or_start)), Int(_index(stop) - sign), Int(step_value))


class RangeTransformer(BaseTransformer):
    rewriter = make_forwarding_rewriter("range", "_poop_range", "_poop_range_cls")
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_range": _poop_range,
        "_poop_range_cls": builtin_alias(Range, _poop_range, "range"),
    }
