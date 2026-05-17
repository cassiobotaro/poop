import os as _stdlib_os

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.os import OS, Env, Process
from poop.types.path import Path
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- OS namespace ---


def test_os_urandom_returns_bytes() -> None:
    result = OS.urandom(Int(8))
    assert isinstance(result, Bytes)
    assert len(result._value) == 8


def test_os_cpu_count_returns_int_or_none() -> None:
    n = OS.cpu_count()
    assert isinstance(n, Int) or n is none


def test_os_process_cpu_count() -> None:
    n = OS.process_cpu_count()
    assert isinstance(n, Int) or n is none


@pytest.mark.skipif(
    not hasattr(_stdlib_os, "getloadavg"),
    reason="getloadavg is Unix-only",
)
def test_os_getloadavg_returns_tuple_of_float() -> None:
    result = OS.getloadavg()
    assert isinstance(result, Tuple)
    assert result.len() == Int(3)


def test_os_constants_are_ints() -> None:
    for attr in ("F_OK", "R_OK", "W_OK", "X_OK"):
        assert isinstance(getattr(OS, attr), Int)
    for attr in ("O_RDONLY", "O_WRONLY", "O_RDWR", "O_APPEND", "O_CREAT", "O_TRUNC"):
        assert isinstance(getattr(OS, attr), Int)


def test_os_separators_are_str() -> None:
    for attr in ("sep", "linesep", "pathsep", "devnull"):
        assert isinstance(getattr(OS, attr), Str)


def test_os_class_refs() -> None:
    assert OS.process is Process
    assert OS.env is Env


# --- Process namespace ---


def test_process_pid_matches_stdlib() -> None:
    assert Process.pid() == Int(_stdlib_os.getpid())


def test_process_ppid_returns_int() -> None:
    assert isinstance(Process.ppid(), Int)


def test_process_uid_gid_euid_egid_return_ints() -> None:
    assert isinstance(Process.uid(), Int)
    assert isinstance(Process.gid(), Int)
    assert isinstance(Process.euid(), Int)
    assert isinstance(Process.egid(), Int)


def test_process_umask_round_trip() -> None:
    old = Process.umask(Int(0o022))
    try:
        assert isinstance(old, Int)
    finally:
        Process.umask(old)


def test_process_getcwd_returns_path() -> None:
    assert isinstance(Process.getcwd(), Path)


def test_process_chdir_round_trip(tmp_path) -> None:
    original = Process.getcwd()
    try:
        assert Process.chdir(Str(str(tmp_path))) is none
        assert str(Process.getcwd()) == str(tmp_path)
    finally:
        Process.chdir(original)


# --- Env namespace ---


def test_env_set_get_has(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POOP_TEST_FOO", raising=False)
    assert Env.has(Str("POOP_TEST_FOO")) is false
    assert Env.set(Str("POOP_TEST_FOO"), Str("bar")) is none
    assert Env.has(Str("POOP_TEST_FOO")) is true
    assert Env.get(Str("POOP_TEST_FOO")) == Str("bar")
    Env.unset(Str("POOP_TEST_FOO"))
    assert Env.has(Str("POOP_TEST_FOO")) is false


def test_env_get_default() -> None:
    assert Env.get(Str("POOP_MISSING_KEY"), Str("fallback")) == Str("fallback")


def test_env_get_missing_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POOP_MISSING_KEY", raising=False)
    assert Env.get(Str("POOP_MISSING_KEY")) is none


def test_env_keys_returns_set() -> None:
    assert isinstance(Env.keys(), Set)


def test_env_values_returns_list() -> None:
    assert isinstance(Env.values(), List)


def test_env_as_dict_returns_dict() -> None:
    assert isinstance(Env.as_dict(), Dict)


def test_env_unset_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POOP_NEVER_SET", raising=False)
    assert Env.unset(Str("POOP_NEVER_SET")) is none


# --- Interpreter integration ---


def test_os_via_interpreter() -> None:
    Interpreter().run_source("os.cpu_count().print()")


def test_process_via_interpreter() -> None:
    Interpreter().run_source("process.pid().print()")


def test_env_via_interpreter() -> None:
    Interpreter().run_source("env.has('PATH').print()")
