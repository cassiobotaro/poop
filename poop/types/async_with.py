from inspect import isawaitable
from typing import TYPE_CHECKING, final

from poop.types import mirrors
from poop.types._message import describe_operand
from poop.types._sentinel import MISSING
from poop.types.block import _require_block
from poop.types.coroutine import Coroutine
from poop.types.error import Error
from poop.types.exceptions import poop_class_of
from poop.types.none import none
from poop.types.object import Object
from poop.types.with_ import protocol_of

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


@final
class AsyncWith(Object, name="AsyncWith"):
    """`With` for an asynchronous context manager: `async with`, as a message.

    `do` answers a coroutine and runs nothing. Awaiting it enters the manager,
    awaits the coroutine the body answers while the manager is still entered,
    and exits, so a failure at the body's await reaches `__aexit__`
    (`doc/adr/0080-asyncwith-and-an-awaited-try-run-at-the-await-the-synchronous-forms-refuse-a-coroutine.md`).
    `__aexit__` receives what `With`'s `__exit__` does: the mirror class, the
    `Error`, and `none` for the traceback.
    """

    __slots__ = ("_cm_block", "_done")

    def __init__(
        self, cm_block: Callable[[], object] | MISSING = MISSING, /, *extra: object
    ) -> None:
        # Counted in POOP's words, as `With` counts: left to CPython, a wrong
        # count would name `__init__` and a positional argument.
        if cm_block is MISSING or extra:
            given = "nothing" if cm_block is MISSING else f"{len(extra) + 1} arguments"
            raise mirrors.TypeError(
                f"AsyncWith takes one block, got {given} — write AsyncWith(lambda: …)"
            )
        self._cm_block = _require_block(
            cm_block, "the manager argument", "write AsyncWith(lambda: …)"
        )
        self._done = False

    def do(self, body_block: Callable[[object], object]) -> Coroutine:
        _require_block(body_block, "the body argument", "write .do(lambda resource: …)")
        if self._done:
            raise mirrors.RuntimeError(
                "AsyncWith has already run; create a new AsyncWith instance to "
                "run again."
            )
        self._done = True
        cm_block = self._cm_block
        # Single-use, as `With`: the executed instance does not pin what the
        # manager block captured.
        del self._cm_block
        return Coroutine._of(_entered(cm_block, body_block))

    def __str__(self) -> str:
        return "AsyncWith"


def _slot(cm: object, slot: str, answer: object) -> Awaitable[object]:
    """What the manager's `slot` answered, refused unless it can be awaited.

    Left to `await`, the refusal would name the class alone, not the slot.
    CPython's `async with` sentence names both as dunders, `__aenter__` and
    `__await__`.
    """
    if not isawaitable(answer):
        raise mirrors.TypeError(
            f"{type(cm).__name__}'s asynchronous {slot} answered "
            f"{describe_operand(answer)}, which cannot be awaited — write it as "
            "async def"
        )
    return answer


async def _entered(
    cm_block: Callable[[], object], body_block: Callable[[object], object]
) -> object:
    cm = cm_block()
    enter, exit_ = protocol_of(
        cm, ("__aenter__", "__aexit__"), "asynchronous context manager"
    )
    value = await _slot(cm, "enter", enter(cm))
    answer: object = none
    result: object = none
    try:
        answer = body_block(value)
        if isawaitable(answer):
            result = await answer
    except BaseException as e:
        handled = await _slot(cm, "exit", exit_(cm, poop_class_of(e), Error(e), none))
        if not handled:
            raise
        # As in `With`: a swallowed failure leaves no value to answer.
        return none
    await _slot(cm, "exit", exit_(cm, none, none, none))
    if not isawaitable(answer):
        # After the exit, as `With` refuses a coroutine body: the manager was
        # entered, so it is left the way a body that finished would leave it.
        raise mirrors.TypeError(
            "the AsyncWith body must answer a coroutine, got "
            f"{describe_operand(answer)} — use With for a body that does not await"
        )
    return result
