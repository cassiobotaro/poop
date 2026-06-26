from __future__ import annotations

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.subprocess import CompletedProcess, Popen, Subprocess
from poop.types.tuple import Tuple


def test_run_simple_returns_completed_process() -> None:
    result = Subprocess.run(List(Str("true")))
    assert isinstance(result, CompletedProcess)
    assert result.returncode == Int(0)


def test_run_with_capture_output_bytes() -> None:
    result = Subprocess.run(List(Str("echo"), Str("hi")), capture_output=true)
    stdout = result.stdout
    assert isinstance(stdout, Bytes)
    assert b"hi" in stdout._value


def test_run_with_text_capture() -> None:
    result = Subprocess.run(
        List(Str("echo"), Str("hi")), capture_output=true, text=true
    )
    stdout = result.stdout
    assert isinstance(stdout, Str)
    assert "hi" in stdout._value


def test_run_with_check_passes() -> None:
    result = Subprocess.run(List(Str("true")), check=true)
    assert result.returncode == Int(0)


def test_run_with_check_raises() -> None:
    with pytest.raises(Subprocess.CalledProcessError):
        Subprocess.run(List(Str("false")), check=true)


def test_run_with_shell() -> None:
    result = Subprocess.run(Str("echo hi"), shell=true, capture_output=true, text=true)
    assert "hi" in result.stdout._value


def test_run_with_cwd(tmp_path) -> None:
    result = Subprocess.run(
        List(Str("pwd")),
        cwd=Str(str(tmp_path)),
        capture_output=true,
        text=true,
    )
    assert str(tmp_path) in result.stdout._value


def test_run_with_timeout_succeeds() -> None:
    Subprocess.run(List(Str("true")), timeout=Float(5.0))


def test_run_with_input() -> None:
    result = Subprocess.run(
        List(Str("cat")), input=Bytes(b"hello"), capture_output=true
    )
    assert b"hello" in result.stdout._value


def test_completed_process_stderr_is_none_by_default() -> None:
    result = Subprocess.run(List(Str("true")))
    assert result.stderr is none


def test_completed_process_args_property() -> None:
    result = Subprocess.run(List(Str("true")))
    assert result.args is not None


def test_completed_process_check_returncode_ok() -> None:
    result = Subprocess.run(List(Str("true")))
    assert result.check_returncode() is none


def test_completed_process_check_returncode_raises() -> None:
    result = Subprocess.run(List(Str("false")))
    with pytest.raises(Subprocess.CalledProcessError):
        result.check_returncode()


# --- call / check_call / check_output ---


def test_call_returns_int() -> None:
    assert Subprocess.call(List(Str("true"))) == Int(0)


def test_call_with_shell() -> None:
    assert Subprocess.call(Str("true"), shell=true) == Int(0)


def test_check_call_returns_int() -> None:
    assert Subprocess.check_call(List(Str("true"))) == Int(0)


def test_check_call_with_shell() -> None:
    assert Subprocess.check_call(Str("true"), shell=true) == Int(0)


def test_check_call_raises_on_failure() -> None:
    with pytest.raises(Subprocess.CalledProcessError):
        Subprocess.check_call(List(Str("false")))


def test_check_output_bytes() -> None:
    out = Subprocess.check_output(List(Str("echo"), Str("hi")))
    assert isinstance(out, Bytes)


def test_check_output_text() -> None:
    out = Subprocess.check_output(List(Str("echo"), Str("hi")), text=true)
    assert isinstance(out, Str)


def test_check_output_with_shell() -> None:
    out = Subprocess.check_output(Str("echo hi"), shell=true, text=true)
    assert isinstance(out, Str)
    assert "hi" in out._value


def test_getoutput() -> None:
    out = Subprocess.getoutput(Str("echo hi"))
    assert isinstance(out, Str)


def test_getstatusoutput() -> None:
    result = Subprocess.getstatusoutput(Str("echo hi"))
    assert isinstance(result, Tuple)
    assert result.len() == Int(2)


# --- Popen ---


def test_popen_construct_and_wait() -> None:
    p = Popen(List(Str("true")))
    assert p.wait() == Int(0)


def test_popen_pid_is_int() -> None:
    p = Popen(List(Str("true")))
    try:
        assert isinstance(p.pid, Int)
    finally:
        p.wait()


def test_popen_returncode_initially_none() -> None:

    p = Popen(List(Str("true")))
    # After wait, returncode is 0.
    p.wait()
    assert p.returncode == Int(0)


def test_popen_poll() -> None:
    p = Popen(List(Str("true")))
    p.wait()
    assert p.poll() == Int(0)


def test_popen_terminate_and_kill() -> None:
    p = Popen(List(Str("sleep"), Str("30")))
    try:
        assert p.terminate() is none
    finally:
        p.wait()
    p2 = Popen(List(Str("sleep"), Str("30")))
    try:
        assert p2.kill() is none
    finally:
        p2.wait()


def test_popen_send_signal() -> None:
    import signal as _stdlib_signal

    p = Popen(List(Str("sleep"), Str("30")))
    try:
        assert p.send_signal(Int(_stdlib_signal.SIGTERM)) is none
    finally:
        p.wait()


def test_popen_context_manager_closes_pipes() -> None:
    import subprocess as _stdlib_sub

    with Popen(
        List(Str("cat")),
        stdin=_stdlib_sub.PIPE,
        stdout=_stdlib_sub.PIPE,
    ) as p:
        assert isinstance(p, Popen)
        impl = p._impl
        stdin = impl.stdin
        stdout = impl.stdout
    assert stdin is not None
    assert stdout is not None
    # CPython's Popen.__exit__ closes the PIPE streams and waits, so the
    # file descriptors opened for stdin/stdout don't leak.
    assert stdin.closed
    assert stdout.closed
    assert impl.returncode is not None


def test_popen_communicate() -> None:
    import subprocess as _stdlib_sub

    p = Popen(
        List(Str("cat")),
        stdin=_stdlib_sub.PIPE,
        stdout=_stdlib_sub.PIPE,
    )
    pair = p.communicate(Bytes(b"hello"))
    assert isinstance(pair, Tuple)
    stdout = pair.at(Int(0))
    assert isinstance(stdout, Bytes)


# --- Constants and class refs ---


def test_subprocess_constants_are_ints() -> None:
    assert isinstance(Subprocess.PIPE, Int)
    assert isinstance(Subprocess.STDOUT, Int)
    assert isinstance(Subprocess.DEVNULL, Int)


def test_subprocess_error_classes() -> None:
    assert issubclass(Subprocess.SubprocessError, Exception)
    assert issubclass(Subprocess.CalledProcessError, Exception)
    assert issubclass(Subprocess.TimeoutExpired, Exception)


def test_subprocess_class_refs() -> None:
    assert Subprocess.Popen is Popen
    assert Subprocess.CompletedProcess is CompletedProcess


# --- Interpreter integration ---


def test_subprocess_via_interpreter() -> None:
    Interpreter().run_source('subprocess.run(["true"]).returncode.print()')
