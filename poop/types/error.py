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
from poop.types.object import MessageNotUnderstood, Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


def _answered_by_the_class_side(kind: type, name: str) -> bool:
    """Whether `name` is a class-side message `kind` really answers.

    Read off the metaclass MRO's dicts, not through `getattr`: a refusing
    descriptor raises when asked, and `class_side_read_refusal` — the shape the
    `BaseException` leftovers use — would look identical to a message otherwise.
    """
    found = class_side_named(type(kind), name)
    return found is not None and not found.refuses


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

        Answering a `Str` here was the same substitution `class_name()` used to
        make, a name standing in for a class, and it survived only because POOP
        had no class objects to answer with. It does now.
        """
        return poop_class_of(self._exception)

    def class_(self) -> PoopExcMeta:
        """Transparent identity: answer the wrapped exception's class.

        An `Error` stands in for the exception it caught, so `e.class_()` and
        the `class_name()` built on it answer that exception's class — mirroring
        Python's `except IndexError as e`, where `type(e)` is `IndexError`, not
        some wrapper. Without this, `class_name()` leaked the internal `Error`.
        `kind()` is the explicit spelling of the same answer.
        """
        return self.kind()

    def is_instance(self, type_: type) -> Boolean:
        """Transparent identity, like `class_` — ask the exception, not the wrapper.

        `Object.is_instance` asks about `self`, and `self` is the `Error`, so a
        handler that fired *because* the error is a `ValueError` was told it is
        not one: `e.is_instance(ValueError)` answered false, `e.is_instance(
        Exception)` answered false, and `e.is_instance(Object)` answered true —
        the answer was about the wrapper, which `class_`'s docstring says is the
        one object an `Error` must never be.

        It cost a program the natural multi-way handler. `if` is banned and
        `except_` chaining needs the kinds up front, so catching `Exception`
        once and dispatching inside on `e.is_instance(...)` is how POOP spells
        several `except` clauses — and that shape silently took no branch.

        `unalias` is applied here rather than delegated to `Object.is_instance`
        because the check runs against `kind()`, not against `self`.
        """
        return to_boolean(
            issubclass(self.kind(), a_class(unalias(type_), "is_instance"))
        )

    def raise_(self) -> Never:
        """Signal this error again — POOP's substitute for a bare `raise`.

        `raise_` is a *class-side* message, so `e.raise_()` used to answer
        `ValueError does not understand #raise_` — the exact sentence
        `PoopExcMeta.raise_`'s docstring quotes as the bug it was written to
        remove, still reachable one spelling over, and false besides:
        `ValueError` does understand `#raise_`.

        What that fix bought was `e.kind().raise_(e.message())`, which builds a
        **new** exception. This re-raises the one that was caught, so its
        identity, its notes and its traceback survive — which is what a handler
        that logs and rethrows actually wants, and what Python's bare `raise`
        does.
        """
        raise self._exception

    def _state(self) -> dict[str, object]:
        """The public state a program's own exception class stored on the instance.

        A mirror carries no state of its own (`__slots__ = ()`), so this is
        empty for every builtin kind; a `class Field(Exception)` whose
        `__init__` wrote `self.code` fills it, and that is exactly what a
        handler reading `e.code` was refused. `is_message` keeps the rule
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
        # `Error` per handler, so the error `raise_` re-signals compared
        # unequal to the one first caught — while its docstring sells exactly
        # that identity surviving. The shape `_MethodBlock` uses for a bound
        # method: equal by what is wrapped, never by the wrapper.
        return to_boolean(
            isinstance(other, Error) and self._exception is other._exception
        )

    def __hash__(self) -> int:
        return hash(self._exception)

    def does_not_understand(self, name: Str) -> object:
        """Refuse under the caught exception's name, not the wrapper's.

        The fourth spelling of the leak `class_()`, `class_name()` and
        `__str__` already close. `explain` labels a receiver with
        `type(obj).__name__`, and the cloak below answers `object` — right for
        the class, wrong for an instance that stands for exactly one exception
        and names it everywhere else. Python agrees: `except ZeroDivisionError
        as e` reports `'ZeroDivisionError' object has no attribute 'zzz'`.

        The transparent label is also what made this refusal falsifiable. It is
        composed from `self.kind().name()` — a `#name` sent to the class, and
        answered — so `e.name()` was refused by a sentence built out of the very
        message it claimed the receiver did not understand. `name` and
        `superclass` are class-side and an `Error` is an instance, so they are
        still refused; what changes is that the sentence says so. POOP already
        words the opposite direction (`#upper asks an instance; send it to one`)
        and had nothing for this one.
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
        # worded the same here, where the reader was told "a caught error
        # answers #message" and then handed the generic sentence by the error.
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
        # construct, so it had no business printing itself — the same argument
        # that closed the `class_name()` leak above. An empty message degrades
        # to the bare class name rather than a dangling colon, as `_describe`
        # does for the same reason.
        name = self.kind().name()
        message = self.message()
        return f"{name}: {message}" if str(message) else str(name)
