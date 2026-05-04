from typing import final

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

    def kind(self) -> Str:
        return Str(type(self._exception).__name__)

    def __str__(self) -> str:
        return f"Error({self._exception})"
