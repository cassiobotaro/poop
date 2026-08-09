"""The refusal for a collection changed while it was being iterated.

CPython answers `dictionary changed size during iteration`: `dictionary` is not
a word POOP uses — the receiver prints as a `dict` — and "during iteration"
describes a `for` loop the program did not write. It wrote `#do`.

Only a *native* `RuntimeError` is reworded. POOP raises its own through
`MIRRORS["RuntimeError"]` (the block-ran-off-the-end message in `Map`/`Filter`,
`Try`'s already-executed refusal), and user code can only raise the mirror too,
since `RuntimeError.raise_(...)` names it — so a native one reaching an
iteration site came from CPython.
"""

from typing import Any

from poop.types.exceptions import MIRRORS, PoopExcMeta


def reword_if_native(exc: RuntimeError, label: str) -> Exception:
    """`exc` itself when it is already POOP's, or the mirrored rewording.

    The test is on `type(exc)`, not `isinstance`: `PoopExcMeta` makes a mirror
    match its native twin on purpose — that is how `except_(RuntimeError, h)`
    catches a raw one — so `isinstance(exc, MIRRORS["RuntimeError"])` is true
    of *every* RuntimeError and would have reworded POOP's own messages.
    """
    if isinstance(type(exc), PoopExcMeta):
        return exc
    return MIRRORS["RuntimeError"](
        f"{label} changed while it was being iterated — "
        "finish the iteration before adding or removing elements"
    )


def iterating(receiver: Any) -> str:
    """The label for a receiver being iterated — its own cloaked name."""
    return type(receiver).__name__
