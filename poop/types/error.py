from typing import Any, final

from poop.types._cloak import cloak
from poop.types._message import poop_message
from poop.types.object import Object
from poop.types.string import Str


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

    def does_not_understand(self, name: str) -> Any:
        """Refuse under the caught exception's name, not the wrapper's.

        The fourth spelling of the leak `class_()`, `class_name()` and
        `__str__` already close. `explain` labels a receiver with
        `type(obj).__name__`, and the cloak below answers `object` — right for
        the class, wrong for an instance that stands for exactly one exception
        and names it everywhere else. Python agrees: `except ZeroDivisionError
        as e` reports `'ZeroDivisionError' object has no attribute 'zzz'`.
        """
        from poop.types._selectors import explain
        from poop.types.object import MessageNotUnderstood

        label = str(self.kind().name())
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
