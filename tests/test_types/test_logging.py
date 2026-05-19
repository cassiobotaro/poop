import logging as _stdlib_logging
import tempfile
from pathlib import Path as _PyPath

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.logging import (
    Filter,
    Formatter,
    Handler,
    Logger,
    Logging,
    LogRecord,
)
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str


def test_get_logger_returns_logger() -> None:
    logger = Logging.getLogger(Str("poop.test"))
    assert isinstance(logger, Logger)


def test_get_logger_no_name_returns_root() -> None:
    assert isinstance(Logging.getLogger(), Logger)


def test_level_constants() -> None:
    assert Logging.CRITICAL == Int(50)
    assert Logging.ERROR == Int(40)
    assert Logging.WARNING == Int(30)
    assert Logging.INFO == Int(20)
    assert Logging.DEBUG == Int(10)
    assert Logging.NOTSET == Int(0)


def test_get_level_name() -> None:
    assert Logging.getLevelName(Logging.INFO) == Str("INFO")


def test_add_level_name() -> None:
    assert Logging.addLevelName(Int(45), Str("CUSTOM")) is none
    assert Logging.getLevelName(Int(45)) == Str("CUSTOM")


def test_basic_config_returns_none() -> None:
    assert Logging.basicConfig() is none


def test_basic_config_with_args() -> None:
    assert (
        Logging.basicConfig(
            level=Logging.DEBUG, format=Str("%(levelname)s:%(message)s")
        )
        is none
    )


def test_basic_config_filename_and_filemode(tmp_path: _PyPath) -> None:
    log_path = tmp_path / "app.log"
    assert (
        Logging.basicConfig(
            filename=Path(Str(str(log_path))),
            filemode=Str("w"),
            level=Logging.INFO,
            force=true,
        )
        is none
    )
    logger = Logging.getLogger(Str("poop.test.filemode"))
    logger.info(Str("hello"))
    for h in _stdlib_logging.getLogger().handlers:
        h.flush()
    assert "hello" in log_path.read_text()


def test_basic_config_datefmt_and_style() -> None:
    assert (
        Logging.basicConfig(
            format=Str("{asctime} {message}"),
            datefmt=Str("%Y"),
            style=Str("{"),
            force=true,
        )
        is none
    )


def test_basic_config_force_resets_root_handlers() -> None:
    Logging.basicConfig(level=Logging.WARNING, force=true)
    handlers_before = list(_stdlib_logging.getLogger().handlers)
    assert handlers_before  # basicConfig installed one
    Logging.basicConfig(level=Logging.DEBUG, force=true)
    # force=True replaces the prior handler set.
    handlers_after = _stdlib_logging.getLogger().handlers
    assert len(handlers_after) == 1
    assert handlers_after[0] is not handlers_before[0]


def test_basic_config_handlers_list() -> None:
    h = Logging.NullHandler()
    assert Logging.basicConfig(handlers=List(h), force=true) is none
    assert h in _stdlib_logging.getLogger().handlers


def test_basic_config_encoding_and_errors(tmp_path: _PyPath) -> None:
    log_path = tmp_path / "utf8.log"
    assert (
        Logging.basicConfig(
            filename=Path(Str(str(log_path))),
            filemode=Str("w"),
            encoding=Str("utf-8"),
            errors=Str("replace"),
            level=Logging.INFO,
            force=true,
        )
        is none
    )


def test_basic_config_level_accepts_str() -> None:
    assert Logging.basicConfig(level=Str("DEBUG"), force=true) is none
    assert _stdlib_logging.getLogger().level == _stdlib_logging.DEBUG


# --- Logger methods ---


def test_logger_set_level() -> None:
    logger = Logging.getLogger(Str("poop.test.level"))
    assert logger.setLevel(Logging.WARNING) is none


def test_logger_set_level_with_str() -> None:
    logger = Logging.getLogger(Str("poop.test.level2"))
    assert logger.setLevel(Str("INFO")) is none


def test_logger_get_effective_level() -> None:
    logger = Logging.getLogger(Str("poop.test.effective"))
    assert isinstance(logger.getEffectiveLevel(), Int)


def test_logger_isenabledfor() -> None:
    logger = Logging.getLogger(Str("poop.test.enabled"))
    assert isinstance(logger.isEnabledFor(Logging.INFO), Boolean)


def test_logger_emits_log_messages() -> None:
    logger = Logging.getLogger(Str("poop.test.emit"))
    # All these should return none.
    assert logger.debug(Str("d")) is none
    assert logger.info(Str("i")) is none
    assert logger.warning(Str("w")) is none
    assert logger.error(Str("e")) is none
    assert logger.critical(Str("c")) is none


def test_logger_exception() -> None:
    logger = Logging.getLogger(Str("poop.test.exception"))
    try:
        raise ValueError("oops")
    except ValueError:
        assert logger.exception(Str("oops")) is none


def test_logger_log_with_level() -> None:
    logger = Logging.getLogger(Str("poop.test.log"))
    assert logger.log(Logging.INFO, Str("hi")) is none


def test_logger_propagate_and_set() -> None:
    logger = Logging.getLogger(Str("poop.test.propagate"))
    assert isinstance(logger.propagate, Boolean)
    from poop.types.boolean import false

    logger.propagate = false
    assert logger.propagate is false


def test_logger_handlers_initially_empty() -> None:
    logger = Logging.getLogger(Str("poop.test.handlers"))
    # Brand-new logger has no handlers by default
    assert isinstance(logger.handlers(), List)


# --- Handlers ---


def test_stream_handler_returns_handler() -> None:
    h = Logging.StreamHandler()
    assert isinstance(h, Handler)


def test_null_handler_returns_handler() -> None:
    assert isinstance(Logging.NullHandler(), Handler)


def test_file_handler_returns_handler() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = _PyPath(td) / "log.txt"
        h = Logging.FileHandler(Str(str(path)))
        try:
            assert isinstance(h, Handler)
        finally:
            h.close()


def test_handler_set_level() -> None:
    h = Logging.StreamHandler()
    assert h.setLevel(Logging.INFO) is none


def test_handler_set_formatter() -> None:
    h = Logging.StreamHandler()
    f = Formatter(fmt=Str("%(levelname)s:%(message)s"))
    assert h.setFormatter(f) is none


def test_logger_add_and_remove_handler() -> None:
    logger = Logging.getLogger(Str("poop.test.addhandler"))
    h = Logging.NullHandler()
    assert logger.addHandler(h) is none
    handlers = logger.handlers()
    assert handlers.len()._value >= 1
    assert logger.removeHandler(h) is none


# --- Formatter ---


def test_formatter_default() -> None:
    assert isinstance(Formatter(), Formatter)


def test_formatter_with_fmt() -> None:
    f = Formatter(fmt=Str("%(message)s"))
    assert isinstance(f, Formatter)


# --- Module-level convenience ---


def test_module_debug_info_warning_error_critical() -> None:
    assert Logging.debug(Str("d")) is none
    assert Logging.info(Str("i")) is none
    assert Logging.warning(Str("w")) is none
    assert Logging.error(Str("e")) is none
    assert Logging.critical(Str("c")) is none


# --- Class refs ---


def test_logging_class_refs() -> None:
    assert Logging.Logger is Logger
    assert Logging.Handler is Handler
    assert Logging.Formatter is Formatter
    assert Logging.Filter is Filter


# --- Subclassing surface (bridge consumer) ---


def test_filter_subclass_returning_poop_boolean() -> None:
    captured: list[_stdlib_logging.LogRecord] = []

    class OnlyWarnings(Filter):
        def filter(self, record):  # type: ignore[override,no-untyped-def]
            captured.append(record)
            return true if record.levelno >= _stdlib_logging.WARNING else false

    logger = Logging.getLogger(Str("poop.test.filter.subclass"))
    logger.addHandler(Logging.NullHandler())
    logger.addFilter(OnlyWarnings())
    logger.setLevel(Logging.DEBUG)

    logger.info(Str("not interesting"))
    logger.warning(Str("hot"))

    assert len(captured) == 2
    assert any(r.levelname == "WARNING" for r in captured)


def test_formatter_subclass_returning_poop_str() -> None:
    class ShoutFormatter(Formatter):
        def format(self, record):  # type: ignore[override,no-untyped-def]
            return Str(record.getMessage().upper() + "!!")

    f = ShoutFormatter()
    rec = _stdlib_logging.LogRecord(
        name="x",
        level=_stdlib_logging.INFO,
        pathname="",
        lineno=0,
        msg="hello",
        args=None,
        exc_info=None,
    )
    assert f.format(rec) == "HELLO!!"


def test_handler_subclass_emits() -> None:
    seen: list[str] = []

    class CaptureHandler(Handler):
        def emit(self, record):  # type: ignore[override,no-untyped-def]
            seen.append(record.getMessage())

    h = CaptureHandler()
    logger = Logging.getLogger(Str("poop.test.handler.subclass"))
    logger.addHandler(h)
    logger.setLevel(Logging.DEBUG)

    logger.info(Str("captured-1"))
    logger.warning(Str("captured-2"))

    assert "captured-1" in seen
    assert "captured-2" in seen
    logger.removeHandler(h)


def test_handler_is_stdlib_handler() -> None:
    # POOP Handler IS a CPython logging.Handler — no _impl wrapping.
    assert issubclass(Handler, _stdlib_logging.Handler)
    assert issubclass(Filter, _stdlib_logging.Filter)
    assert issubclass(Formatter, _stdlib_logging.Formatter)
    assert isinstance(Logging.NullHandler(), _stdlib_logging.Handler)


def test_formatter_constructor_kwargs() -> None:
    f = Formatter(
        fmt=Str("%(levelname)s|%(message)s"),
        datefmt=Str("%Y"),
        style=Str("%"),
        validate=true,
    )
    rec = _stdlib_logging.LogRecord(
        name="x",
        level=_stdlib_logging.WARNING,
        pathname="",
        lineno=0,
        msg="msg",
        args=None,
        exc_info=None,
    )
    assert f.format(rec) == "WARNING|msg"


# --- Interpreter integration ---


def test_logging_via_interpreter() -> None:
    Interpreter().run_source(
        'logger = logging.getLogger("poop.test.via")\nlogger.info("hi")'
    )


# --- LogRecord wrapper ---


def test_log_record_exposes_poop_typed_fields() -> None:
    raw = _stdlib_logging.LogRecord(
        name="test",
        level=_stdlib_logging.INFO,
        pathname="x.py",
        lineno=10,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    from poop.types.logging import LogRecord

    rec = LogRecord(raw)
    assert rec.name == Str("test")
    assert rec.levelname == Str("INFO")
    assert rec.levelno == Int(_stdlib_logging.INFO)
    assert rec.getMessage() == Str("hello world")


def test_logging_log_record_class_ref() -> None:
    from poop.types.logging import LogRecord

    assert Logging.LogRecord is LogRecord


# --- LoggerAdapter ---


def test_logger_adapter_passes_extra_through() -> None:
    from poop.types.dict import Dict
    from poop.types.logging import LoggerAdapter

    logger = Logging.getLogger(Str("poop.test.adapter"))
    adapter = LoggerAdapter(logger, Dict().at_put(Str("user"), Str("alice")))
    assert adapter.info(Str("hi")) is none


def test_logging_logger_adapter_class_ref() -> None:
    from poop.types.logging import LoggerAdapter

    assert Logging.LoggerAdapter is LoggerAdapter


# --- Module-level toggles ---


def test_logging_raise_exceptions_toggle() -> None:
    original = Logging.raiseExceptions
    try:
        Logging.raiseExceptions = false
        assert Logging.raiseExceptions is false
        assert _stdlib_logging.raiseExceptions is False
        Logging.raiseExceptions = true
        assert Logging.raiseExceptions is true
    finally:
        Logging.raiseExceptions = original


def test_logging_log_threads_toggle() -> None:
    original = Logging.logThreads
    try:
        Logging.logThreads = false
        assert _stdlib_logging.logThreads is False
    finally:
        Logging.logThreads = original


# --- Module-level functions ---


def test_logging_disable_returns_none() -> None:
    assert Logging.disable(Logging.WARNING) is none
    # Re-enable everything for subsequent tests.
    Logging.disable(Int(0))


def test_logging_capture_warnings_returns_none() -> None:
    assert Logging.captureWarnings(true) is none
    Logging.captureWarnings(false)


def test_make_log_record_from_dict() -> None:
    from poop.types.dict import Dict
    from poop.types.logging import LogRecord

    d = Dict().at_put(Str("name"), Str("x")).at_put(Str("levelno"), Int(20))
    rec = Logging.makeLogRecord(d)
    assert isinstance(rec, LogRecord)
    assert rec.name == Str("x")


def test_get_level_names_mapping_includes_INFO() -> None:
    from poop.types.dict import Dict

    mapping = Logging.getLevelNamesMapping()
    assert isinstance(mapping, Dict)
    assert mapping.at(Str("INFO")) == Logging.INFO


def test_get_handler_names_returns_list() -> None:
    out = Logging.getHandlerNames()
    assert isinstance(out, List)


# --- Style classes / Filterer ---


def test_logging_style_class_refs_match_stdlib() -> None:
    assert Logging.PercentStyle is _stdlib_logging.PercentStyle
    assert Logging.StrFormatStyle is _stdlib_logging.StrFormatStyle
    assert Logging.StringTemplateStyle is _stdlib_logging.StringTemplateStyle


def test_logging_filterer_class_ref() -> None:
    assert Logging.Filterer is _stdlib_logging.Filterer


# --- BufferingFormatter ---


def test_buffering_formatter_constructs() -> None:
    from poop.types.logging import BufferingFormatter

    bf = BufferingFormatter()
    assert isinstance(bf, _stdlib_logging.BufferingFormatter)


# --- LogRecord properties (raise coverage on the property cluster) ---


_LOG_RECORD_PATHNAME = str(_PyPath(__file__))


def _make_log_record() -> _stdlib_logging.LogRecord:
    return _stdlib_logging.LogRecord(
        name="poop.test",
        level=_stdlib_logging.WARNING,
        pathname=_LOG_RECORD_PATHNAME,
        lineno=42,
        msg="hi %s",
        args=("there",),
        exc_info=None,
        func="my_func",
    )


def _make_record() -> LogRecord:
    return LogRecord(_make_log_record())


def test_log_record_name_msg_args() -> None:
    r = _make_record()
    assert r.name == Str("poop.test")
    assert isinstance(r.msg, Str)
    assert isinstance(r.args, object)  # Tuple via to_poop


def test_log_record_level_props() -> None:
    r = _make_record()
    assert r.levelname == Str("WARNING")
    assert r.levelno == Int(_stdlib_logging.WARNING)


def test_log_record_location_props() -> None:
    r = _make_record()
    assert r.pathname == Str(_LOG_RECORD_PATHNAME)
    assert isinstance(r.filename, Str)
    assert isinstance(r.module, Str)
    assert r.lineno == Int(42)
    assert r.funcName == Str("my_func")


def test_log_record_created_is_float() -> None:
    from poop.types.float import Float

    assert isinstance(_make_record().created, Float)


def test_log_record_thread_process_props() -> None:
    r = _make_record()
    assert isinstance(r.thread, Int) or r.thread is none
    assert isinstance(r.threadName, Str) or r.threadName is none
    assert isinstance(r.process, Int) or r.process is none
    assert isinstance(r.processName, Str) or r.processName is none


def test_log_record_get_message() -> None:
    assert _make_record().getMessage() == Str("hi there")


# --- LoggerAdapter ---


def test_logger_adapter_debug_info_warning_error_critical() -> None:
    from poop.types.dict import Dict
    from poop.types.logging import LoggerAdapter

    logger = Logging.getLogger(Str("poop.adapter.test"))
    extras = Dict()
    extras.at_put(Str("user"), Str("alice"))
    adapter = LoggerAdapter(logger, extras)
    assert adapter.debug(Str("d")) is none
    assert adapter.info(Str("i")) is none
    assert adapter.warning(Str("w")) is none
    assert adapter.error(Str("e")) is none
    assert adapter.critical(Str("c")) is none


def test_logger_adapter_log_and_setlevel() -> None:
    from poop.types.logging import LoggerAdapter

    logger = Logging.getLogger(Str("poop.adapter.log"))
    adapter = LoggerAdapter(logger)
    assert adapter.log(Int(_stdlib_logging.INFO), Str("msg")) is none
    assert adapter.setLevel(Int(_stdlib_logging.WARNING)) is none
    assert adapter.setLevel(Str("DEBUG")) is none
