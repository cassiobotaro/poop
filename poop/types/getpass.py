import getpass as _getpass
from typing import TYPE_CHECKING

from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class Getpass:
    """Namespace mirroring Python's `getpass` module.

    Two reads — `getpass.getpass(prompt='Password: ', stream=None)`
    and `getpass.getuser()` — both return POOP `Str`. The Python
    `GetPassWarning` (emitted when echo can't be suppressed) is **not
    surfaced** in POOP: POOP has no warning concept (see
    `warnings` in proposals.md). The underlying CPython call still
    emits the warning to stderr; POOP user code just cannot catch
    or filter it.
    """

    @staticmethod
    def getpass(prompt: Str | None = None, stream: NoneClass | None = None) -> Str:
        from poop.types.none import NoneClass as _NoneClass

        prompt_value = "Password: " if prompt is None else prompt._value
        # POOP only models terminal `none` for the stream parameter;
        # the underlying getpass.getpass accepts file-like or None.
        if stream is None or isinstance(stream, _NoneClass):
            return Str(_getpass.getpass(prompt_value))
        return Str(_getpass.getpass(prompt_value, stream))

    @staticmethod
    def getuser() -> Str:
        return Str(_getpass.getuser())
