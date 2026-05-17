from __future__ import annotations

import logging as _logging
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


def _unwrap_level(level: Int | Str) -> Any:
    return level._value if isinstance(level, Int) else level._value


class Formatter(Object):
    """Wraps Python's `logging.Formatter`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any = None, fmt: Str | None = None) -> None:
        if impl is not None:
            self._impl = impl
        elif fmt is None:
            self._impl = _logging.Formatter()
        else:
            self._impl = _logging.Formatter(fmt._value)


class Handler(Object):
    """Wraps Python's `logging.Handler` — base / `StreamHandler` / `FileHandler`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def setLevel(self, level: Int | Str) -> NoneClass:
        self._impl.setLevel(_unwrap_level(level))
        return none

    def setFormatter(self, formatter: Formatter) -> NoneClass:
        self._impl.setFormatter(formatter._impl)
        return none


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

    def addHandler(self, h: Handler) -> NoneClass:
        self._impl.addHandler(h._impl)
        return none

    def removeHandler(self, h: Handler) -> NoneClass:
        self._impl.removeHandler(h._impl)
        return none

    def handlers(self) -> List:
        return List(*(Handler(h) for h in self._impl.handlers))

    @property
    def propagate(self) -> Boolean:
        return true if self._impl.propagate else false

    @propagate.setter
    def propagate(self, value: Boolean) -> None:
        self._impl.propagate = bool(value)


class Logging:
    """Namespace mirroring (a curated subset of) Python's `logging` module."""

    Logger: ClassVar[type[Logger]] = Logger
    Handler: ClassVar[type[Handler]] = Handler
    Formatter: ClassVar[type[Formatter]] = Formatter

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
        *, level: Int | None = None, format: Str | None = None
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        if level is not None:
            kwargs["level"] = level._value
        if format is not None:
            kwargs["format"] = format._value
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

    @staticmethod
    def StreamHandler() -> Handler:
        return Handler(_logging.StreamHandler())

    @staticmethod
    def FileHandler(path: Path | Str) -> Handler:
        p = path._value if isinstance(path, Str) else str(path)
        return Handler(_logging.FileHandler(p))

    @staticmethod
    def NullHandler() -> Handler:
        return Handler(_logging.NullHandler())
