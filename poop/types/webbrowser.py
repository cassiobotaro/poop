import webbrowser as _webbrowser
from collections.abc import Callable
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.none import NoneClass, none
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

    Concrete browser controller classes (`Chrome`/`Mozilla`/...) are
    exposed as static factories that return a `Browser`. `register`
    accepts a POOP callable as `constructor`; the result is unwrapped
    via the standard Block↔callable bridge so CPython sees a callable
    returning a `BaseBrowser` while POOP code returns a `Browser`.
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

    # Concrete controllers — each takes the path to a browser executable
    # and returns a POOP `Browser` wrapping the underlying `BaseBrowser`.

    @staticmethod
    def GenericBrowser(name: Str) -> Browser:
        return Browser(_webbrowser.GenericBrowser(name._value))

    @staticmethod
    def BackgroundBrowser(name: Str) -> Browser:
        return Browser(_webbrowser.BackgroundBrowser(name._value))

    @staticmethod
    def UnixBrowser(name: Str = Str("")) -> Browser:
        return Browser(_webbrowser.UnixBrowser(name._value))

    @staticmethod
    def Mozilla(name: Str = Str("")) -> Browser:
        return Browser(_webbrowser.Mozilla(name._value))

    @staticmethod
    def Chrome(name: Str = Str("")) -> Browser:
        return Browser(_webbrowser.Chrome(name._value))

    @staticmethod
    def Chromium(name: Str = Str("")) -> Browser:
        # ty's webbrowser stub omits Chromium/Edge/Epiphany; they exist at
        # runtime as subclasses of UnixBrowser.
        cls: Any = _webbrowser.Chromium  # ty: ignore[unresolved-attribute]
        return Browser(cls(name._value))

    @staticmethod
    def Edge(name: Str = Str("")) -> Browser:
        cls: Any = _webbrowser.Edge  # ty: ignore[unresolved-attribute]
        return Browser(cls(name._value))

    @staticmethod
    def Opera(name: Str = Str("")) -> Browser:
        return Browser(_webbrowser.Opera(name._value))

    @staticmethod
    def Epiphany(name: Str = Str("")) -> Browser:
        cls: Any = _webbrowser.Epiphany  # ty: ignore[unresolved-attribute]
        return Browser(cls(name._value))

    @staticmethod
    def Elinks(name: Str = Str("")) -> Browser:
        return Browser(_webbrowser.Elinks(name._value))

    @staticmethod
    def Konqueror() -> Browser:
        return Browser(_webbrowser.Konqueror())

    @staticmethod
    def register(
        name: Str,
        constructor: Callable[..., Any] | None = None,
        instance: Browser | None = None,
        *,
        preferred: Boolean = false,
    ) -> NoneClass:
        # constructor is a POOP-callable returning a Browser; adapt to a
        # Python callable returning a BaseBrowser for CPython's registry.
        py_ctor: Callable[..., _webbrowser.BaseBrowser] | None
        if constructor is None:
            py_ctor = None
        else:

            def py_ctor(*args: Any, **kwargs: Any) -> _webbrowser.BaseBrowser:
                result = constructor(*args, **kwargs)
                if isinstance(result, Browser):
                    return result._impl
                # POOP code may have returned a raw BaseBrowser already;
                # accept either shape.
                return result

        py_instance = None if instance is None else instance._impl
        _webbrowser.register(
            name._value, py_ctor, py_instance, preferred=bool(preferred)
        )
        return none
