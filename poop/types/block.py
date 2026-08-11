from collections.abc import Callable
from functools import partial
from inspect import Parameter, signature
from types import MethodType
from typing import TYPE_CHECKING, Any, cast

from poop.types._cloak import cloak
from poop.types._message import article
from poop.types.exceptions import MIRRORS
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass


def _count(n: int) -> str:
    return f"{n} argument" if n == 1 else f"{n} arguments"


def _require_block(value: Any, role: str, hint: str) -> Any:
    """`value`, or a refusal naming the argument rather than the call.

    Checked at the boundary, where the argument has a name, instead of at the
    deferred call, where CPython answers `'int' object is not callable` — true
    of every POOP object, and silent about what was expected. `With` is the
    one worth optimizing for: it takes a block that *answers* a manager, and
    passing the manager itself is the obvious first attempt.

    The same argument proposal 2 settled for `With`: resolve what you need
    before running anything, so the failure lands where the mistake was
    written rather than after a deferred block has had side effects.
    """
    if not callable(value):
        raise MIRRORS["TypeError"](
            f"{role} must be a block, got {article(type(value).__name__)} — {hint}"
        )
    return value


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
            #
            # The two failures are separated before rewording. Folding them
            # together — `len(args) + len(kwargs)` — reported a keyword the
            # block cannot take as a *count* mismatch whose count matched, so
            # `.do(item=x)` answered `block expects 1 argument, got 1`. The
            # count message now sees `len(args)` alone, which makes that
            # sentence unrepresentable.
            keyword_fault = self._keyword_message(args, kwargs)
            if keyword_fault is not None:
                raise MIRRORS["TypeError"](keyword_fault) from None
            raise MIRRORS["TypeError"](self._arity_message(len(args))) from None

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        """A block found on a *class* binds to the receiver, as a method does.

        `set_attr` on a class is sanctioned — proposal 2 refused it only for
        POOP's own builtins, precisely so a program can extend the classes it
        defines — and the one thing a reader reaches for it with did not work:
        `C.set_attr("greet", lambda self: "hi")` then `C().greet()` answered
        `block expects 1 argument, got 0`, because the block was handed back
        untouched and the receiver never passed. The refusal was the worst
        part: the reader wrote a one-argument block and was told it got none.

        Defining only `__get__` makes this a *non-data* descriptor, which is
        exactly Python's own split and needs no special case: consulted for a
        class attribute, skipped for one found in the instance's `__dict__`.
        So a `Block` held as *state* (`self.callback = lambda: …`) still reads
        back as itself — that half already worked and must keep working.

        Answers `self` when read off the class (`C.greet`), as a function does.

        The receiver is bound onto *this block*, not onto `_fn`: a wrong-arity
        call then fails inside `__call__` above and is worded from the block
        the program actually wrote (`block expects 0 arguments, got 1` for a
        zero-argument block installed on a class, which is the mistake Python
        reports too). Binding `_fn` directly hid that — `signature` refuses an
        over-bound `partial`, so `_accepted` answered nothing and the refusal
        degraded to `block does not accept 0 arguments`, about a call that
        passed none.
        """
        if instance is None:
            return self
        return Block(partial(self, instance))

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

    def _keyword_message(
        self, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> str | None:
        """The refusal for a *keyword* failure, or `None` if the count is at fault.

        `__call__` used to hand `_arity_message` `len(args) + len(kwargs)`, so
        every keyword mistake was reported as a count mismatch — and the count
        came out right:

            (lambda x: x)(nope=1)        # block expects 1 argument, got 1
            (lambda x: x)(1, x=2)        # block expects 1 argument, got 1
            (lambda x, *, k: x)(1)       # block expects 1 argument, got 1

        A sentence stating two equal numbers and refusing anyway teaches
        nothing, and none of the three mentioned the actual fault. CPython names
        all three (`got an unexpected keyword argument 'nope'`, `got multiple
        values for argument 'x'`, `missing 1 required keyword-only argument:
        'k'`), which POOP is right to reword — `<lambda>` and "positional
        argument" are both banned by the wording sweep — and was wrong to
        collapse into one number.

        Answers `None` when the signature cannot be read, which is the case
        `_accepted` degrades on too, and when nothing about the keywords is
        wrong — leaving `_arity_message` the positional count alone, which makes
        `expects 1, got 1` unrepresentable.
        """
        try:
            params = list(signature(self._fn).parameters.values())
        except TypeError, ValueError:
            return None
        takes_any = any(param.kind is Parameter.VAR_KEYWORD for param in params)
        by_keyword = [
            param
            for param in params
            if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
        ]
        accepted = {param.name for param in by_keyword}
        if not takes_any:
            unexpected = next((name for name in kwargs if name not in accepted), None)
            if unexpected is not None:
                return f"block does not take a keyword argument {unexpected!r}"
        # A name filled positionally *and* by keyword. Only the parameters the
        # positional arguments actually reached can collide.
        positional = [
            param.name
            for param in params
            if param.kind
            in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        ][: len(args)]
        duplicate = next((name for name in positional if name in kwargs), None)
        if duplicate is not None:
            return f"block already got {duplicate!r} as a positional argument"
        missing = next(
            (
                param.name
                for param in params
                if param.kind is Parameter.KEYWORD_ONLY
                and param.default is Parameter.empty
                and param.name not in kwargs
            ),
            None,
        )
        if missing is not None:
            return f"block needs a keyword argument {missing!r}"
        return None

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
        from poop.types._argument import a_block

        # Through `self()`, not `self._fn()`: a condition block of the wrong
        # arity would otherwise answer CPython's wording from here.
        body = a_block(body, "while_true", param="")
        while bool(self()):
            body()
        return none

    def while_false(self, body: Block) -> NoneClass:
        from poop.types._argument import a_block

        body = a_block(body, "while_false", param="")
        while not bool(self()):
            body()
        return none

    def __str__(self) -> str:
        return "<block>"

    __repr__ = __str__


class _MethodBlock(Block):
    """A method read off an object, wrapped so it answers messages.

    `Object.__getattribute__` hands one of these back for `"abc".upper`, so a
    method read by writing it reads back as the same kind of object one
    fetched by name does — `_as_block`'s rule, which had only been wired into
    `get_attr`, the spelling almost nobody writes.

    It answers everything a `Block` answers and calls like a *method*: the
    arity refusal stays CPython's, because `cloak` has already worded that one
    for a message (`str.upper() takes 1 positional argument but 2 were
    given`), and `Block`'s rewording would replace the message's own name with
    the word `block`. Skipping the rewrite also keeps `inspect.signature` out
    of the failure path — it evaluates a wrapper's annotations, and half of
    `poop/types/` declares names under `TYPE_CHECKING` only.
    """

    __slots__ = ()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._fn(*args, **kwargs)

    # Equality by the pair the bound method wraps — its receiver and its
    # underlying function — which is exactly what CPython's bound method
    # compares, and for the same reason: a program has to be able to ask "is
    # this the same callback?".
    #
    # `Object` compares by identity, and `__getattribute__` builds a fresh
    # wrapper on every read, so `s.upper == s.upper` was false — as were
    # `.hash()` and every registry built on either. The shape a reader hits is
    # storing `obj.on_change` and later asking whether it is already
    # registered: the answer was no, every time, and nothing warned.
    #
    # `Block` itself keeps identity deliberately. It wraps a lambda, and two
    # lambdas with the same body are different blocks in Smalltalk as in
    # Python — so this lives here rather than on the base.
    def _identity(self) -> tuple[Any, Any]:
        # `_fn` is declared `Callable[..., Any]` on the base, and is always a
        # `MethodType` here: `Object.__getattribute__` builds a `_MethodBlock`
        # only for `type(value) is MethodType`.
        method = cast("MethodType", self._fn)
        return (method.__self__, method.__func__)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        if not isinstance(other, _MethodBlock):
            return to_boolean(False)
        return to_boolean(self._identity() == other._identity())

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self == other) else true

    def __hash__(self) -> int:
        # Consistent with __eq__ above, as CPython's bound method is: equal
        # methods must hash equally or `set`/`dict` membership contradicts `==`.
        return hash(self._identity())


# A POOP block is a wrapped lambda, and CPython's class for a lambda is
# `function` (`type(lambda: 0).__name__`). Answer that name so `class_()` and
# `class_name()` mirror Python instead of leaking the `poop.types.block.Block`
# path — the same cloak every other wrapper applies.
cloak(Block, "function")
cloak(_MethodBlock, "function")
