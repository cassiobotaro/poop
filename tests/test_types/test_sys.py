import sys as _stdlib_sys

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.sys import Stdin, Stdout, Sys
from poop.types.tuple import Tuple


def test_sys_executable_returns_path() -> None:
    result = Sys.executable
    assert isinstance(result, Path)


def test_sys_platform_returns_str() -> None:
    assert Sys.platform == Str(_stdlib_sys.platform)


def test_sys_version_returns_str() -> None:
    assert Sys.version == Str(_stdlib_sys.version)


def test_sys_version_info_returns_tuple() -> None:
    vi = Sys.version_info
    assert isinstance(vi, Tuple)
    assert vi.len() == Int(5)


def test_sys_maxsize_is_int() -> None:
    assert Sys.maxsize == Int(_stdlib_sys.maxsize)


def test_sys_byteorder_is_str() -> None:
    assert Sys.byteorder == Str(_stdlib_sys.byteorder)


def test_sys_modules_returns_dict() -> None:
    result = Sys.modules
    assert isinstance(result, Dict)
    assert result.includes(Str("sys"))


def test_sys_path_returns_list() -> None:
    result = Sys.path
    assert isinstance(result, List)


def test_sys_recursion_limit_round_trip() -> None:
    original = Sys.getrecursionlimit()
    Sys.setrecursionlimit(Int(2000))
    try:
        assert Sys.getrecursionlimit() == Int(2000)
    finally:
        Sys.setrecursionlimit(original)


def test_sys_implementation_is_python_object() -> None:
    impl = Sys.implementation
    assert impl.name in ("cpython", "pypy")


def test_sys_flags_float_int_hash_thread_info() -> None:
    assert Sys.flags is _stdlib_sys.flags
    assert Sys.float_info is _stdlib_sys.float_info
    assert Sys.int_info is _stdlib_sys.int_info
    assert Sys.hash_info is _stdlib_sys.hash_info
    assert Sys.thread_info is _stdlib_sys.thread_info


def test_sys_exit_raises() -> None:
    with pytest.raises(SystemExit):
        Sys.exit(Int(0))


def test_sys_exit_with_str() -> None:
    with pytest.raises(SystemExit):
        Sys.exit(Str("done"))


def test_sys_exit_no_arg() -> None:
    with pytest.raises(SystemExit):
        Sys.exit()


# --- argv / stdout / stderr / stdin ---


def test_sys_argv_returns_list_of_str() -> None:
    result = Sys.argv
    assert isinstance(result, List)
    if result.len()._value > 0:
        assert isinstance(result.at(Int(0)), Str)


def test_stdout_returns_stdout_wrapper() -> None:
    assert isinstance(Sys.stdout, Stdout)


def test_stderr_returns_stdout_wrapper() -> None:
    assert isinstance(Sys.stderr, Stdout)


def test_stdin_returns_stdin_wrapper() -> None:
    assert isinstance(Sys.stdin, Stdin)


def test_stdout_write_and_writeln(capsys: pytest.CaptureFixture[str]) -> None:
    out = Sys.stdout
    out.write(Str("hello"))
    out.writeln(Str(" world"))
    captured = capsys.readouterr()
    assert captured.out == "hello world\n"


def test_stdout_writeln_no_arg(capsys: pytest.CaptureFixture[str]) -> None:
    out = Sys.stdout
    out.writeln()
    captured = capsys.readouterr()
    assert captured.out == "\n"


def test_stdout_flush_returns_none() -> None:
    assert Sys.stdout.flush() is none


def test_stdout_isatty_returns_boolean() -> None:
    assert isinstance(Sys.stdout.isatty(), Boolean)


def test_stdin_isatty_returns_boolean() -> None:
    assert isinstance(Sys.stdin.isatty(), Boolean)


def test_stdin_read_via_mock() -> None:
    import io

    custom = Stdin(io.StringIO("hello\nworld\n"))
    assert custom.read() == Str("hello\nworld\n")


def test_stdin_readline_via_mock() -> None:
    import io

    custom = Stdin(io.StringIO("hello\nworld\n"))
    assert custom.readline() == Str("hello\n")


def test_stdin_readline_with_size() -> None:
    import io

    custom = Stdin(io.StringIO("hello world"))
    assert custom.readline(Int(3)) == Str("hel")


def test_stdin_readlines_via_mock() -> None:
    import io

    custom = Stdin(io.StringIO("a\nb\n"))
    assert custom.readlines() == List(Str("a\n"), Str("b\n"))


def test_stdin_read_with_size() -> None:
    import io

    custom = Stdin(io.StringIO("abcdefg"))
    assert custom.read(Int(3)) == Str("abc")


def test_stdin_iteration() -> None:
    import io

    custom = Stdin(io.StringIO("a\nb\n"))
    assert list(custom) == [Str("a\n"), Str("b\n")]


# --- Interpreter integration ---


def test_sys_platform_via_interpreter() -> None:
    Interpreter().run_source("sys.platform.print()")


def test_sys_argv_via_interpreter() -> None:
    Interpreter().run_source("sys.argv")
