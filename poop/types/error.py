from typing import TYPE_CHECKING, Any, Never, final

from poop.types._cloak import cloak
from poop.types._message import poop_message
from poop.types.meta import class_side
from poop.types.object import Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


def _answered_by_the_class_side(kind: type, name: str) -> bool:
    """Whether `name` is a class-side message `kind` really answers.

    Read off the metaclass MRO's dicts, not through `getattr`: a refusing
    descriptor raises when asked, and `class_side_read_refusal` — the shape the
    `BaseException` leftovers use — would look identical to a message otherwise.
    """
    for metaclass in type(kind).__mro__:
        attr = vars(metaclass).get(name)
        if isinstance(attr, class_side):
            return not attr.refuses
    return False


@final
class Error(Object):
    """Wraps a caught Python exception as a POOP object."""

    __slots__ = ("_exception",)

    def __init__(self, exception: BaseException) -> None:
        self._exception = exception

    def message(self) -> Str:
        # Through `poop_message`, like the uncaught path: a handler reading
        # `e.message()` must not be the one place Python's operator wording
        # still shows through.
        return Str(poop_message(self._exception))

    def kind(self) -> Any:
        """The exception's class — the class itself, not its name.

        Answering a `Str` here was the same substitution `class_name()` used to
        make, a name standing in for a class, and it survived only because POOP
        had no class objects to answer with. It does now.
        """
        from poop.types.exceptions import poop_class_of

        return poop_class_of(self._exception)

    def class_(self) -> Any:
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
        from poop.types._alias import unalias
        from poop.types._argument import a_class
        from poop.types.boolean import to_boolean

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

    def does_not_understand(self, name: str) -> Any:
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
        from poop.types._selectors import explain
        from poop.types.object import MessageNotUnderstood

        kind = self.kind()
        label = str(kind.name())
        # `vars` down the metaclass MRO rather than `hasattr`: asking the class
        # is what raises here for a refusing descriptor, and a refusal is not an
        # answer. Only a real class-side message earns the redirect.
        if _answered_by_the_class_side(kind, name):
            raise MessageNotUnderstood(
                f"{label} does not understand #{name} — "
                f"#{name} asks a class; send it to #kind()",
                name=name,
                obj=self,
            )
        raise MessageNotUnderstood(explain(self, name, label), name=name, obj=self)

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


# The third spelling of the same leak `class_()` and `__str__` above already
# closed: CPython builds a wrong-arity message from the *function's* qualname,
# so `e.message(1)` blamed `Error.message()` — the `poop.types` detail those
# two docstrings call "a name user code can neither name nor construct".
# `object` because an `Error` stands in for whatever it caught, so no single
# exception name is true for the class.
cloak(Error, "object")
