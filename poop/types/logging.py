from __future__ import annotations

import logging as _logging
import logging.config as _logging_config
from typing import TYPE_CHECKING, Any, ClassVar, cast

from poop.types._bridge import to_python
from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types.boolean import Boolean, false, to_boolean, true
from poop.types.dict import Dict
from poop.types.int import Int

if TYPE_CHECKING:
    from poop.types.float import Float
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


class LogRecord(Object):
    """Wraps Python's `logging.LogRecord` — a single log event.

    Exposes the common fields as POOP-typed attributes; `getMessage()`
    formats the message lazily. POOP user code that overrides
    `Filter.filter` / `Handler.emit` / `Formatter.format` can choose to
    receive the raw `_logging.LogRecord` (default) or wrap it via
    `LogRecord(record)` to access POOP-typed fields.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: _logging.LogRecord) -> None:
        self._impl = impl

    @property
    def name(self) -> Str:
        return Str(self._impl.name)

    @property
    def msg(self) -> Object:
        from poop.types._bridge import to_poop

        return to_poop(self._impl.msg)

    @property
    def args(self) -> Object:
        from poop.types._bridge import to_poop

        return to_poop(self._impl.args)

    @property
    def levelname(self) -> Str:
        return Str(self._impl.levelname)

    @property
    def levelno(self) -> Int:
        return Int(self._impl.levelno)

    @property
    def pathname(self) -> Str:
        return Str(self._impl.pathname)

    @property
    def filename(self) -> Str:
        return Str(self._impl.filename)

    @property
    def module(self) -> Str:
        return Str(self._impl.module)

    @property
    def lineno(self) -> Int:
        return Int(self._impl.lineno)

    @property
    def funcName(self) -> Str:
        return Str(self._impl.funcName)

    @property
    def created(self) -> Float:
        from poop.types.float import Float

        return Float(self._impl.created)

    @property
    def thread(self) -> Int | NoneClass:
        return none if self._impl.thread is None else Int(self._impl.thread)

    @property
    def threadName(self) -> Str | NoneClass:
        n = self._impl.threadName
        return none if n is None else Str(n)

    @property
    def process(self) -> Int | NoneClass:
        return none if self._impl.process is None else Int(self._impl.process)

    @property
    def processName(self) -> Str | NoneClass:
        n = self._impl.processName
        return none if n is None else Str(n)

    def getMessage(self) -> Str:
        return Str(self._impl.getMessage())


class BufferingFormatter(_logging.BufferingFormatter):
    """Wraps Python's `logging.BufferingFormatter` — formats a buffered
    batch of records with optional header/footer."""

    def __init__(self, linefmt: Formatter | None = None) -> None:
        super().__init__(linefmt if linefmt is not None else None)


class _LevelMethodsMixin:
    """Level methods shared by `Logger` and `LoggerAdapter` — both
    forward to an `_impl` exposing the stdlib logger API."""

    __slots__ = ()

    _impl: Any

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

    def log(self, level: Int, msg: Str) -> NoneClass:
        self._impl.log(level._value, msg._value)
        return none

    def setLevel(self, level: Int | Str) -> NoneClass:
        self._impl.setLevel(to_python(level))
        return none


class LoggerAdapter(_LevelMethodsMixin, Object):
    """Wraps Python's `logging.LoggerAdapter` — pass an `extra` dict
    through every log call on a wrapped Logger."""

    __slots__ = ("_impl",)

    def __init__(self, logger: Logger, extra: Dict | NoneClass | None = None) -> None:
        extra_dict: dict[str, Any] | None
        if extra is None or isinstance(extra, NoneClass):
            extra_dict = None
        else:
            extra_dict = cast(dict[str, Any], to_python(extra))
        self._impl = _logging.LoggerAdapter(logger._impl, extra_dict)


class _LoggingMeta(type):
    """Metaclass that exposes module-level toggles
    (`raiseExceptions` / `logThreads` / `logProcesses` /
    `logMultiprocessing` / `logAsyncioTasks`) as class-level properties
    so `Logging.X = false` reaches the underlying `_logging.X`."""

    @property
    def raiseExceptions(cls) -> Boolean:
        return to_boolean(_logging.raiseExceptions)

    @raiseExceptions.setter
    def raiseExceptions(cls, value: Boolean) -> None:
        _logging.raiseExceptions = bool(value)

    @property
    def logThreads(cls) -> Boolean:
        return to_boolean(_logging.logThreads)

    @logThreads.setter
    def logThreads(cls, value: Boolean) -> None:
        _logging.logThreads = bool(value)

    @property
    def logProcesses(cls) -> Boolean:
        return to_boolean(_logging.logProcesses)

    @logProcesses.setter
    def logProcesses(cls, value: Boolean) -> None:
        _logging.logProcesses = bool(value)

    @property
    def logMultiprocessing(cls) -> Boolean:
        return to_boolean(_logging.logMultiprocessing)

    @logMultiprocessing.setter
    def logMultiprocessing(cls, value: Boolean) -> None:
        _logging.logMultiprocessing = bool(value)

    @property
    def logAsyncioTasks(cls) -> Boolean:
        return to_boolean(getattr(_logging, "logAsyncioTasks", False))

    @logAsyncioTasks.setter
    def logAsyncioTasks(cls, value: Boolean) -> None:
        # Python 3.12+ exposes logAsyncioTasks. setattr keeps us flexible
        # for older versions where it might be absent.
        setattr(_logging, "logAsyncioTasks", bool(value))  # noqa: B010


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
        super().__init__(_logging.NOTSET if level is None else to_python(level))

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_emit = cls.__dict__.get("emit")
        if user_emit is None:
            return

        def wrapped_emit(self: _logging.Handler, record: _logging.LogRecord) -> None:
            user_emit(self, record)

        cls.emit = wrapped_emit  # type: ignore[method-assign]

    def setLevel(self, level: Int | Str) -> NoneClass:  # type: ignore[override]
        super().setLevel(to_python(level))
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
            filename = str(path)
        _logging.FileHandler.__init__(
            self,
            filename,
            mode="a" if mode is None else mode._value,
            encoding=None if encoding is None else encoding._value,
            delay=bool(delay),
            errors=None if errors is None else errors._value,
        )


class Logger(_ImplWrapperMixin, _LevelMethodsMixin, Object):
    """Wraps Python's `logging.Logger`."""

    __slots__ = ("_impl",)

    def __init__(self, name: Str, level: Int | Str | NoneClass | None = None) -> None:
        # Mirror CPython's logging.Logger(name, level=NOTSET). Internal
        # wrapping of an existing logger uses _from_impl, not this ctor.
        if level is None or isinstance(level, NoneClass):
            self._impl = _logging.Logger(name._value)
        else:
            self._impl = _logging.Logger(name._value, level._value)

    def getEffectiveLevel(self) -> Int:
        return Int(self._impl.getEffectiveLevel())

    def isEnabledFor(self, level: Int) -> Boolean:
        return to_boolean(self._impl.isEnabledFor(level._value))

    def exception(self, msg: Str) -> NoneClass:
        self._impl.exception(msg._value)
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
        return to_boolean(self._impl.propagate)

    @propagate.setter
    def propagate(self, value: Boolean) -> None:
        self._impl.propagate = bool(value)


class Logging(metaclass=_LoggingMeta):
    """Namespace mirroring (a curated subset of) Python's `logging` module.

    Filter, Handler, Formatter inherit from their stdlib counterparts
    via `__init_subclass__` bridging so user subclasses can override
    `filter(record)`, `emit(record)`, `format(record)` in POOP idiom —
    same pattern as `Json.JSONEncoder.default`.

    Module-level toggles (`raiseExceptions`, `logThreads`,
    `logProcesses`, `logMultiprocessing`, `logAsyncioTasks`) are
    exposed as class-level Boolean properties via the metaclass; writes
    update the underlying `_logging.X` module attribute.
    """

    Logger: ClassVar[type[Logger]] = Logger
    Filter: ClassVar[type[Filter]] = Filter
    Handler: ClassVar[type[Handler]] = Handler
    Formatter: ClassVar[type[Formatter]] = Formatter
    StreamHandler: ClassVar[type[StreamHandler]] = StreamHandler
    NullHandler: ClassVar[type[NullHandler]] = NullHandler
    FileHandler: ClassVar[type[FileHandler]] = FileHandler
    LogRecord: ClassVar[type[LogRecord]] = LogRecord
    LoggerAdapter: ClassVar[type[LoggerAdapter]] = LoggerAdapter
    BufferingFormatter: ClassVar[type[BufferingFormatter]] = BufferingFormatter

    # Filterer is `_logging.Filterer` — exposed for `isinstance` checks.
    Filterer: ClassVar[type] = _logging.Filterer

    # Style classes used by Formatter — exposed for completeness; user
    # code rarely instantiates these directly.
    PercentStyle: ClassVar[type] = _logging.PercentStyle
    StrFormatStyle: ClassVar[type] = _logging.StrFormatStyle
    StringTemplateStyle: ClassVar[type] = _logging.StringTemplateStyle

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
            return Logger._from_impl(_logging.getLogger())
        return Logger._from_impl(_logging.getLogger(name._value))

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
            kwargs["filename"] = str(filename)
        if filemode is not None:
            kwargs["filemode"] = filemode._value
        if format is not None:
            kwargs["format"] = format._value
        if datefmt is not None:
            kwargs["datefmt"] = datefmt._value
        if style is not None:
            kwargs["style"] = style._value
        if level is not None:
            kwargs["level"] = to_python(level)
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

    @staticmethod
    def log(level: Int, msg: Str) -> NoneClass:
        _logging.log(level._value, msg._value)
        return none

    @staticmethod
    def exception(msg: Str) -> NoneClass:
        """Log a message with severity `ERROR` plus traceback info on
        the root logger; intended to be called from inside an exception
        handler."""
        _logging.exception(msg._value)
        return none

    @staticmethod
    def disable(level: Int | None = None) -> NoneClass:
        """Disable all logging at or below `level` (default `CRITICAL`)."""
        if level is None:
            _logging.disable()
        else:
            _logging.disable(level._value)
        return none

    @staticmethod
    def captureWarnings(capture: Boolean) -> NoneClass:
        """When `true`, route `warnings.warn` calls through the `py.warnings` logger."""
        _logging.captureWarnings(bool(capture))
        return none

    @staticmethod
    def makeLogRecord(d: Dict) -> LogRecord:
        """Construct a `LogRecord` from a dict (mirrors CPython)."""
        return LogRecord(_logging.makeLogRecord(cast(dict[str, Any], to_python(d))))

    @staticmethod
    def getHandlerByName(name: Str) -> Handler | NoneClass:
        result = _logging.getHandlerByName(name._value)
        return none if result is None else cast(Handler, result)

    @staticmethod
    def getHandlerNames() -> List:
        return List(*(Str(n) for n in _logging.getHandlerNames()))

    @staticmethod
    def getLevelNamesMapping() -> Dict:
        d = Dict()
        for name, level in _logging.getLevelNamesMapping().items():
            d.at_put(Str(name), Int(level))
        return d

    @staticmethod
    def getLogRecordFactory() -> Any:
        return _logging.getLogRecordFactory()

    @staticmethod
    def setLogRecordFactory(factory: Any) -> NoneClass:
        _logging.setLogRecordFactory(factory)
        return none

    @staticmethod
    def getLoggerClass() -> type:
        return _logging.getLoggerClass()

    @staticmethod
    def setLoggerClass(klass: type) -> NoneClass:
        _logging.setLoggerClass(klass)  # ty: ignore[invalid-argument-type]
        return none

    @staticmethod
    def dictConfig(config: Dict) -> NoneClass:
        """Configure logging from a dictionary (mirrors `logging.config.dictConfig`)."""
        _logging_config.dictConfig(cast(dict[str, Any], to_python(config)))
        return none

    @staticmethod
    def fileConfig(
        path: Path | Str,
        defaults: Dict | None = None,
        disable_existing_loggers: Boolean = true,
        encoding: Str | None = None,
    ) -> NoneClass:
        """Configure logging from an INI file (mirrors `logging.config.fileConfig`)."""
        if isinstance(path, Path):
            fname: Any = str(path)
        else:
            fname = path._value
        kwargs: dict[str, Any] = {
            "disable_existing_loggers": bool(disable_existing_loggers),
        }
        if defaults is not None:
            kwargs["defaults"] = cast(dict[str, Any], to_python(defaults))
        if encoding is not None:
            kwargs["encoding"] = encoding._value
        _logging_config.fileConfig(fname, **kwargs)
        return none
