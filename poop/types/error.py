import builtins
from typing import TYPE_CHECKING, Never, final

from poop.types._alias import unalias
from poop.types._argument import a_class
from poop.types._message import poop_message
from poop.types._selectors import explain, is_message, not_understood
from poop.types.block import _as_block
from poop.types.boolean import to_boolean
from poop.types.exceptions import (
    _PYTHON_ATTRIBUTES,
    PoopExcMeta,
    _refuse_python_attribute,
    poop_class_of,
)
from poop.types.list import List
from poop.types.meta import class_side_named
from poop.types.none import none
from poop.types.object import MessageNotUnderstood, Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass


def _answered_by_the_class_side(kind: type, name: str) -> bool:
    """Whether `name` is a class-side message `kind` really answers.

    Read off the metaclass MRO's dicts, not through `getattr`: a refusing
    descriptor raises when asked, and `class_side_read_refusal` — the shape the
    `BaseException` leftovers use — would look identical to a message otherwise.
    """
    found = class_side_named(type(kind), name)
    return found is not None and not found.refuses


def _linked(exception: BaseException | None) -> Error | NoneClass:
    return none if exception is None else Error(exception)


@final
class Error(Object, name="object"):
    """Wraps a caught Python exception as a POOP object."""

    __slots__ = ("_exception",)

    def __init__(self, exception: BaseException) -> None:
        self._exception = exception

    def message(self) -> Str:
        # Through `poop_message`, like the uncaught path: a handler reading
        # `e.message()` must not be the one place Python's operator wording
        # still shows through.
        return Str(poop_message(self._exception))

    def kind(self) -> PoopExcMeta:
        """The exception's class — the class itself, not its name.

        Not a `Str`: `class_()` answers a class rather than a name standing in
        for one, and so does this, since POOP has class objects to answer
        with.
        """
        return poop_class_of(self._exception)

    def class_(self) -> PoopExcMeta:
        """Transparent identity: answer the wrapped exception's class.

        An `Error` stands in for the exception it caught, so `e.class_()` and
        the `class_name()` built on it answer that exception's class — mirroring
        Python's `except IndexError as e`, where `type(e)` is `IndexError`, not
        some wrapper. Without this, `class_name()` would answer the internal
        `Error`.
        `kind()` is the explicit spelling of the same answer.
        """
        return self.kind()

    def is_instance(self, type_: type) -> Boolean:
        """Transparent identity, like `class_` — ask the exception, not the wrapper.

        `Object.is_instance` asks about `self`, and `self` is the `Error`, so it
        would tell a handler that fired *because* the error is a `ValueError`
        that it is not one — an answer about the wrapper, which `class_`'s
        docstring says is the one object an `Error` must never be.

        The multi-way handler depends on it. `if` is banned and `except_`
        chaining needs the kinds up front, so catching `Exception` once and
        dispatching inside on `e.is_instance(...)` is how POOP spells several
        `except` clauses.

        `unalias` is applied here rather than delegated to `Object.is_instance`
        because the check runs against `kind()`, not against `self`.
        """
        return to_boolean(
            issubclass(self.kind(), a_class(unalias(type_), "is_instance"))
        )

    def cause(self) -> Error | NoneClass:
        """The error this one was raised from — `__cause__`, as a message.

        `none` when it was raised from nothing, or from `None`.
        """
        return _linked(self._exception.__cause__)

    def context(self) -> Error | NoneClass:
        """The error being handled when this one was raised — `__context__`.

        `none` when the context was suppressed, which the raw dunder does not
        say: POOP composes its own failures with `raise … from None` while
        CPython's native exception is still being handled, so `__context__`
        would hand a handler CPython's wording (`list index out of range`)
        for almost every error POOP composes. Suppressed is also what the
        uncaught report leaves out, so a handler and the terminal see one
        chain.
        """
        exception = self._exception
        if exception.__suppress_context__:
            return none
        return _linked(exception.__context__)

    def raise_(self) -> Never:
        """Signal this error again — POOP's substitute for a bare `raise`.

        `raise_` is also a *class-side* message, so without this `e.raise_()`
        would answer `ValueError does not understand #raise_` — false, since
        `ValueError` does understand `#raise_`.

        `e.kind().raise_(e.message())` builds a **new** exception. This
        re-raises the one that was caught, so its
        identity, its notes and its traceback survive — which is what a handler
        that logs and rethrows actually wants, and what Python's bare `raise`
        does.
        """
        raise self._exception

    def _state(self) -> dict[str, object]:
        """The public state a program's own exception class stored on the instance.

        A mirror carries no state of its own (`__slots__ = ()`), so this is
        empty for every builtin kind; a `class Field(Exception)` whose
        `__init__` wrote `self.code` fills it, and a handler reads it as
        `e.code`. `is_message` keeps the rule
        `dir` applies everywhere: a private or dunder name is not forwarded.
        """
        return {
            name: value
            for name, value in vars(self._exception).items()
            if is_message(name)
        }

    def dir(self) -> List:
        # The wrapper's messages and the exception's forwarded state, as one
        # listing: `Object.dir` reads `builtins.dir(self)`, which cannot see
        # what `does_not_understand` answers.
        names = sorted(
            {*(n for n in builtins.dir(self) if is_message(n)), *self._state()}
        )
        return List(*(Str(name) for name in names))

    def __eq__(self, other: object) -> Boolean:
        # Two wrappers over one exception are one error: `Try` builds a fresh
        # `Error` per handler, and the error `raise_` re-signals must compare
        # equal to the one first caught, the identity its docstring promises.
        # The shape `_MethodBlock` uses for a bound
        # method: equal by what is wrapped, never by the wrapper.
        return to_boolean(
            isinstance(other, Error) and self._exception is other._exception
        )

    def __hash__(self) -> int:
        return hash(self._exception)

    def does_not_understand(self, name: Str) -> object:
        """Refuse under the caught exception's name, not the wrapper's.

        The same transparency `class_()`, `class_name()` and `__str__` keep.
        `explain` labels a receiver with
        `type(obj).__name__`, and the cloak below answers `object` — right for
        the class, wrong for an instance that stands for exactly one exception
        and names it everywhere else. Python agrees: `except ZeroDivisionError
        as e` reports `'ZeroDivisionError' object has no attribute 'zzz'`.

        The label is composed from `self.kind().name()` — a `#name` sent to the
        class, and answered — so a plain refusal of `e.name()` would be built
        out of the very message it claims the receiver does not understand.
        `name` and `superclass` are class-side and an `Error` is an instance,
        so they are refused, by a sentence that says so: the counterpart of
        `#upper asks an instance; send it to one`.
        """
        raw = str(name)
        # Forwarded before any refusal: the state a program's class attached
        # is the one thing about the exception the wrapper did not know.
        state = self._state()
        if raw in state:
            return _as_block(state[raw])
        kind = self.kind()
        label = str(kind.name())
        # A `BaseException` native the class side already refuses by name —
        # worded the same here: that refusal tells the reader "a caught error
        # answers #message", so the error must not answer the generic sentence.
        native = getattr(kind, "_native", None)
        if raw in _PYTHON_ATTRIBUTES and native is not None and hasattr(native, raw):
            _refuse_python_attribute(kind, raw, _PYTHON_ATTRIBUTES[raw])
        # `vars` down the metaclass MRO rather than `hasattr`: asking the class
        # is what raises here for a refusing descriptor, and a refusal is not an
        # answer. Only a real class-side message earns the redirect.
        if _answered_by_the_class_side(kind, raw):
            raise MessageNotUnderstood(
                not_understood(label, raw, f"#{raw} asks a class; send it to #kind()"),
                name=raw,
                obj=self,
            )
        raise MessageNotUnderstood(explain(self, raw, label), name=raw, obj=self)

    def __str__(self) -> str:
        # Built on the identity `class_()` already answers, not on the wrapper:
        # `Error` is a `poop.types` detail user code can neither name nor
        # construct, so it does not print itself — the same argument `class_()`
        # makes above. An empty message degrades
        # to the bare class name rather than a dangling colon, as `_describe`
        # does for the same reason.
        name = self.kind().name()
        message = self.message()
        return f"{name}: {message}" if str(message) else str(name)
