from typing import Any, final

from poop.types.object import Object
from poop.types.string import Str


@final
class Error(Object):
    """Wraps a caught Python exception as a POOP object."""

    __slots__ = ("_exception",)

    def __init__(self, exception: BaseException) -> None:
        self._exception = exception

    def message(self) -> Str:
        return Str(str(self._exception))

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
