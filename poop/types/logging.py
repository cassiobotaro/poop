from __future__ import annotations

import logging as _logging
from typing import Any, ClassVar, cast

from poop.types._bridge import to_python
from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


def _unwrap_level(level: Int | Str) -> Any:
    return level._value


class Filter(_logging.Filter):
    """POOP wrapper around `logging.Filter`.

    Subclass and override `filter(record)` to allow or drop records.
    The override receives the raw `_logging.LogRecord` (no POOP
    LogRecord wrapper yet) and returns a POOP `Boolean` (or any
    truthy/falsy value) — the bridge unwraps the return to a Python
    `bool`.
    """

    def __init__(self, name: Str | None = None) -> None:
        super().__init__("" if name is None else name._value)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_filter = cls.__dict__.get("filter")
        if user_filter is None:
            return

        def wrapped_filter(self: _logging.Filter, record: _logging.LogRecord) -> bool:
            return bool(user_filter(self, record))

        cls.filter = wrapped_filter  # type: ignore[method-assign]


class Formatter(_logging.Formatter):
    """POOP wrapper around `logging.Formatter`.

    Subclass and override `format(record)` to customise log formatting.
    The override receives the raw `_logging.LogRecord` and returns a
    POOP `Str` (or any value `to_python` can convert) — the bridge
    unwraps the return to a Python `str`.
    """

    def __init__(
        self,
        fmt: Str | None = None,
        datefmt: Str | None = None,
        style: Str | None = None,
        validate: Boolean = true,
        defaults: Dict | None = None,
    ) -> None:
        super().__init__(
            fmt=None if fmt is None else fmt._value,
            datefmt=None if datefmt is None else datefmt._value,
            style=cast(Any, "%" if style is None else style._value),
            validate=bool(validate),
            defaults=None if defaults is None else to_python(defaults),
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_format = cls.__dict__.get("format")
        if user_format is None:
            return

        def wrapped_format(self: _logging.Formatter, record: _logging.LogRecord) -> str:
            result = user_format(self, record)
            if isinstance(result, Str):
                return result._value
            return str(to_python(result))

        cls.format = wrapped_format  # type: ignore[method-assign]


class Handler(_logging.Handler):
    """POOP wrapper around `logging.Handler` (the base class).

    Subclass and override `emit(record)` to define a custom sink.
    The override receives the raw `_logging.LogRecord`; the return
    value is ignored (CPython's `emit` is `void`).

    POOP-divergent methods (`setLevel`, `setFormatter`) keep POOP
    return types (`none`); everything else is inherited from
    `_logging.Handler` directly.
    """

    def __init__(self, level: Int | Str | None = None) -> None:
        super().__init__(_logging.NOTSET if level is None else _unwrap_level(level))

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_emit = cls.__dict__.get("emit")
        if user_emit is None:
            return

        def wrapped_emit(self: _logging.Handler, record: _logging.LogRecord) -> None:
            user_emit(self, record)

        cls.emit = wrapped_emit  # type: ignore[method-assign]

    def setLevel(self, level: Int | Str) -> NoneClass:  # type: ignore[override]
        super().setLevel(_unwrap_level(level))
        return none

    def setFormatter(self, fmt: _logging.Formatter | None) -> NoneClass:  # type: ignore[override]
        super().setFormatter(fmt)
        return none

    def addFilter(self, filter: _logging.Filter) -> NoneClass:  # type: ignore[override]
        super().addFilter(filter)
        return none

    def removeFilter(self, filter: _logging.Filter) -> NoneClass:  # type: ignore[override]
        super().removeFilter(filter)
        return none


class StreamHandler(_logging.StreamHandler, Handler):
    """POOP wrapper around `logging.StreamHandler`."""


class NullHandler(_logging.NullHandler, Handler):
    """POOP wrapper around `logging.NullHandler`."""


class FileHandler(_logging.FileHandler, Handler):
    """POOP wrapper around `logging.FileHandler`."""

    def __init__(
        self,
        path: Path | Str,
        mode: Str | None = None,
        encoding: Str | None = None,
        delay: Boolean = false,
        errors: Str | None = None,
    ) -> None:
        if isinstance(path, Str):
            filename = path._value
        else:
            filename = str(path._path)
        _logging.FileHandler.__init__(
            self,
            filename,
            mode="a" if mode is None else mode._value,
            encoding=None if encoding is None else encoding._value,
            delay=bool(delay),
            errors=None if errors is None else errors._value,
        )


class Logger(Object):
    """Wraps Python's `logging.Logger`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def setLevel(self, level: Int | Str) -> NoneClass:
        self._impl.setLevel(_unwrap_level(level))
        return none

    def getEffectiveLevel(self) -> Int:
        return Int(self._impl.getEffectiveLevel())

    def isEnabledFor(self, level: Int) -> Boolean:
        return true if self._impl.isEnabledFor(level._value) else false

    def debug(self, msg: Str) -> NoneClass:
        self._impl.debug(msg._value)
        return none

    def info(self, msg: Str) -> NoneClass:
        self._impl.info(msg._value)
        return none

    def warning(self, msg: Str) -> NoneClass:
        self._impl.warning(msg._value)
        return none

    def error(self, msg: Str) -> NoneClass:
        self._impl.error(msg._value)
        return none

    def critical(self, msg: Str) -> NoneClass:
        self._impl.critical(msg._value)
        return none

    def exception(self, msg: Str) -> NoneClass:
        self._impl.exception(msg._value)
        return none

    def log(self, level: Int, msg: Str) -> NoneClass:
        self._impl.log(level._value, msg._value)
        return none

    def addHandler(self, h: _logging.Handler) -> NoneClass:
        self._impl.addHandler(h)
        return none

    def removeHandler(self, h: _logging.Handler) -> NoneClass:
        self._impl.removeHandler(h)
        return none

    def addFilter(self, f: _logging.Filter) -> NoneClass:
        self._impl.addFilter(f)
        return none

    def removeFilter(self, f: _logging.Filter) -> NoneClass:
        self._impl.removeFilter(f)
        return none

    def handlers(self) -> List:
        return List(*self._impl.handlers)

    @property
    def propagate(self) -> Boolean:
        return true if self._impl.propagate else false

    @propagate.setter
    def propagate(self, value: Boolean) -> None:
        self._impl.propagate = bool(value)


class Logging:
    """Namespace mirroring (a curated subset of) Python's `logging` module.

    Filter, Handler, Formatter inherit from their stdlib counterparts
    via `__init_subclass__` bridging so user subclasses can override
    `filter(record)`, `emit(record)`, `format(record)` in POOP idiom —
    same pattern as `Json.JSONEncoder.default`.
    """

    Logger: ClassVar[type[Logger]] = Logger
    Filter: ClassVar[type[Filter]] = Filter
    Handler: ClassVar[type[Handler]] = Handler
    Formatter: ClassVar[type[Formatter]] = Formatter
    StreamHandler: ClassVar[type[StreamHandler]] = StreamHandler
    NullHandler: ClassVar[type[NullHandler]] = NullHandler
    FileHandler: ClassVar[type[FileHandler]] = FileHandler

    # Level constants
    CRITICAL: ClassVar[Int] = Int(_logging.CRITICAL)
    ERROR: ClassVar[Int] = Int(_logging.ERROR)
    WARNING: ClassVar[Int] = Int(_logging.WARNING)
    INFO: ClassVar[Int] = Int(_logging.INFO)
    DEBUG: ClassVar[Int] = Int(_logging.DEBUG)
    NOTSET: ClassVar[Int] = Int(_logging.NOTSET)

    @staticmethod
    def getLogger(name: Str | None = None) -> Logger:
        if name is None:
            return Logger(_logging.getLogger())
        return Logger(_logging.getLogger(name._value))

    @staticmethod
    def getLevelName(level: Int) -> Str:
        return Str(_logging.getLevelName(level._value))

    @staticmethod
    def addLevelName(level: Int, levelName: Str) -> NoneClass:
        _logging.addLevelName(level._value, levelName._value)
        return none

    @staticmethod
    def basicConfig(
        *,
        filename: Path | None = None,
        filemode: Str | None = None,
        format: Str | None = None,
        datefmt: Str | None = None,
        style: Str | None = None,
        level: Int | Str | None = None,
        handlers: List | None = None,
        force: Boolean = false,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {"force": bool(force)}
        if filename is not None:
            kwargs["filename"] = str(filename._path)
        if filemode is not None:
            kwargs["filemode"] = filemode._value
        if format is not None:
            kwargs["format"] = format._value
        if datefmt is not None:
            kwargs["datefmt"] = datefmt._value
        if style is not None:
            kwargs["style"] = style._value
        if level is not None:
            kwargs["level"] = _unwrap_level(level)
        if handlers is not None:
            kwargs["handlers"] = list(handlers._items)
        if encoding is not None:
            kwargs["encoding"] = encoding._value
        if errors is not None:
            kwargs["errors"] = errors._value
        _logging.basicConfig(**kwargs)
        return none

    @staticmethod
    def debug(msg: Str) -> NoneClass:
        _logging.debug(msg._value)
        return none

    @staticmethod
    def info(msg: Str) -> NoneClass:
        _logging.info(msg._value)
        return none

    @staticmethod
    def warning(msg: Str) -> NoneClass:
        _logging.warning(msg._value)
        return none

    @staticmethod
    def error(msg: Str) -> NoneClass:
        _logging.error(msg._value)
        return none

    @staticmethod
    def critical(msg: Str) -> NoneClass:
        _logging.critical(msg._value)
        return none
