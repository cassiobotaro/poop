from collections.abc import Callable
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any

from poop.types._cloak import cloak
from poop.types.exceptions import MIRRORS
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass


def _count(n: int) -> str:
    return f"{n} argument" if n == 1 else f"{n} arguments"


def _as_block(value: Any) -> Any:
    """A raw Python callable answered by `get_attr`, wrapped as a `Block`.

    An attribute holding state already answers a POOP object; one holding a
    *method* answered CPython's bound method, which understands no message —
    `"abc".get_attr("upper").print()` raised Python's own `AttributeError`
    instead of `does not understand #print`, the last member of the
    `getattr`-substitute family still handing back a native. `Block` is what
    every lambda is already wrapped in, so a method fetched by name reads back
    as the same kind of object a block literal does, callable included.

    A POOP class is left alone: it is callable, but it is already an object
    with its own protocol.
    """
    if callable(value) and not isinstance(value, (Object, type)):
        return Block(value)
    return value


class Block(Object):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return self._fn(*args, **kwargs)
        except TypeError as exc:
            # Which TypeError is this? A signature mismatch is raised by the
            # call machinery *before* the block runs, so its traceback stops
            # at this frame; one raised by the body has the block's own frame
            # below. Only the first is the block's to reword — the second
            # belongs to whatever the body was doing.
            traceback = exc.__traceback__
            if traceback is None or traceback.tb_next is not None:
                raise
            # `from None` on purpose: CPython's wording is the leak. It says
            # `<lambda>()` — the Python name of an object POOP cloaks as
            # `function` and prints as `<block>` — and `positional argument`,
            # a calling convention a block does not have.
            raise MIRRORS["TypeError"](
                self._arity_message(len(args) + len(kwargs))
            ) from None

    def _accepted(self) -> tuple[int, int | None] | None:
        """How many arguments the block takes: (fewest, most), `None` unbounded.

        Answers `None` when CPython cannot introspect the callable — a handful
        of its own builtins carry no signature, and `get_attr` can hand one to
        `_as_block`.
        """
        try:
            params = list(signature(self._fn).parameters.values())
        except TypeError, ValueError:
            return None
        positional = [
            param
            for param in params
            if param.kind
            in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        ]
        required = sum(1 for param in positional if param.default is Parameter.empty)
        variadic = any(param.kind is Parameter.VAR_POSITIONAL for param in params)
        return required, None if variadic else len(positional)

    def _arity_message(self, given: int) -> str:
        accepted = self._accepted()
        if accepted is None:
            return f"block does not accept {_count(given)}"
        fewest, most = accepted
        if most is None:
            expected = f"at least {_count(fewest)}"
        elif fewest == most:
            expected = _count(fewest)
        else:
            expected = f"{fewest} to {_count(most)}"
        return f"block expects {expected}, got {given}"

    def while_true(self, body: Block) -> NoneClass:
        # Through `self()`, not `self._fn()`: a condition block of the wrong
        # arity would otherwise answer CPython's wording from here.
        while bool(self()):
            body()
        return none

    def while_false(self, body: Block) -> NoneClass:
        while not bool(self()):
            body()
        return none

    def __str__(self) -> str:
        return "<block>"

    __repr__ = __str__


# A POOP block is a wrapped lambda, and CPython's class for a lambda is
# `function` (`type(lambda: 0).__name__`). Answer that name so `class_()` and
# `class_name()` mirror Python instead of leaking the `poop.types.block.Block`
# path — the same cloak every other wrapper applies.
cloak(Block, "function")
