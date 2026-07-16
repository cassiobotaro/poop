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

    def __str__(self) -> str:
        return f"Error({self._exception})"
