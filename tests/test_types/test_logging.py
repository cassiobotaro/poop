import logging as _stdlib_logging
import tempfile
from pathlib import Path as _PyPath

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.logging import Formatter, Handler, Logger, Logging
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
    h = Handler(_stdlib_logging.NullHandler())
    assert Logging.basicConfig(handlers=List(h), force=true) is none
    assert h._impl in _stdlib_logging.getLogger().handlers


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
            h._impl.close()


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


def test_formatter_from_impl() -> None:
    f = Formatter(impl=_stdlib_logging.Formatter())
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


# --- Interpreter integration ---


def test_logging_via_interpreter() -> None:
    Interpreter().run_source(
        'logger = logging.getLogger("poop.test.via")\nlogger.info("hi")'
    )
