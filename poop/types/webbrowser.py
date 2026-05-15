import webbrowser as _webbrowser
from typing import ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.string import Str


def _unwrap_int(value: Int | None, default: int) -> int:
    return default if value is None else value._value


def _unwrap_bool(value: Boolean | None, default: bool) -> bool:
    return default if value is None else bool(value)


def _coerce_bool(value: object) -> Boolean:
    return true if value else false


class Browser:
    """Wraps a Python `webbrowser` browser controller.

    Returned by `webbrowser.get(using=none)`. The Python `webbrowser`
    module exposes several concrete browser classes (Chrome, Edge,
    Mozilla, …) — POOP collapses them into a single `Browser` POOP
    type because every concrete class carries the same `.open` /
    `.open_new` / `.open_new_tab` surface. The underlying class
    identity is preserved internally for dispatch.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: _webbrowser.BaseBrowser) -> None:
        self._impl = impl

    @property
    def name(self) -> Str:
        return Str(self._impl.name)

    def open(
        self,
        url: Str,
        new: Int | None = None,
        autoraise: Boolean | None = None,
    ) -> Boolean:
        return _coerce_bool(
            self._impl.open(
                url._value,
                new=_unwrap_int(new, 0),
                autoraise=_unwrap_bool(autoraise, True),
            )
        )

    def open_new(self, url: Str) -> Boolean:
        return _coerce_bool(self._impl.open_new(url._value))

    def open_new_tab(self, url: Str) -> Boolean:
        return _coerce_bool(self._impl.open_new_tab(url._value))

    def __str__(self) -> str:
        return f"Browser({self._impl.name})"

    __repr__ = __str__


class Webbrowser:
    """Namespace mirroring Python's `webbrowser` module.

    The module-level shortcuts (`open`/`open_new`/`open_new_tab`) and
    the controller factory `get(using=none)` are surfaced. The
    `Error` exception class is exposed as a raw Python type so user
    code can pass it to `Try.except_(...)`.

    `register(name, constructor, instance, preferred)` is **deferred
    to Future work** — the `constructor` argument is a Python
    callable returning a `BaseBrowser`, which has no clean POOP
    type-discipline mapping for v1.
    """

    Error: ClassVar[type[Exception]] = _webbrowser.Error

    @staticmethod
    def open(
        url: Str,
        new: Int | None = None,
        autoraise: Boolean | None = None,
    ) -> Boolean:
        return _coerce_bool(
            _webbrowser.open(
                url._value,
                new=_unwrap_int(new, 0),
                autoraise=_unwrap_bool(autoraise, True),
            )
        )

    @staticmethod
    def open_new(url: Str) -> Boolean:
        return _coerce_bool(_webbrowser.open_new(url._value))

    @staticmethod
    def open_new_tab(url: Str) -> Boolean:
        return _coerce_bool(_webbrowser.open_new_tab(url._value))

    @staticmethod
    def get(using: Str | None = None) -> Browser:
        if using is None:
            return Browser(_webbrowser.get())
        return Browser(_webbrowser.get(using._value))
