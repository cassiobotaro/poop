import os as _stdlib_os
from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.os import OS, Environ
from poop.types.path import Path
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- OS: random / CPU helpers ---


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


# --- OS: constants ---


def test_os_constants_are_ints() -> None:
    for attr in ("F_OK", "R_OK", "W_OK", "X_OK"):
        assert isinstance(getattr(OS, attr), Int)
    for attr in ("O_RDONLY", "O_WRONLY", "O_RDWR", "O_APPEND", "O_CREAT", "O_TRUNC"):
        assert isinstance(getattr(OS, attr), Int)


def test_os_separators_are_str() -> None:
    for attr in ("sep", "linesep", "pathsep", "devnull"):
        assert isinstance(getattr(OS, attr), Str)


def test_os_class_ref() -> None:
    assert OS.environ is Environ


# --- OS: process state (now directly on `os`) ---


def test_os_getpid_matches_stdlib() -> None:
    assert OS.getpid() == Int(_stdlib_os.getpid())


def test_os_getppid_returns_int() -> None:
    assert isinstance(OS.getppid(), Int)


def test_os_getuid_gid_euid_egid_return_ints() -> None:
    assert isinstance(OS.getuid(), Int)
    assert isinstance(OS.getgid(), Int)
    assert isinstance(OS.geteuid(), Int)
    assert isinstance(OS.getegid(), Int)


def test_os_umask_round_trip() -> None:
    old = OS.umask(Int(0o022))
    try:
        assert isinstance(old, Int)
    finally:
        OS.umask(old)


def test_os_getcwd_returns_path() -> None:
    assert isinstance(OS.getcwd(), Path)


def test_os_chdir_round_trip(tmp_path) -> None:
    original = OS.getcwd()
    try:
        assert OS.chdir(Str(str(tmp_path))) is none
        assert str(OS.getcwd()) == str(tmp_path)
    finally:
        OS.chdir(original)


# --- os.environ ---


def test_environ_set_get_has(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POOP_TEST_FOO", raising=False)
    assert Environ.has(Str("POOP_TEST_FOO")) is false
    assert Environ.set(Str("POOP_TEST_FOO"), Str("bar")) is none
    assert Environ.has(Str("POOP_TEST_FOO")) is true
    assert Environ.get(Str("POOP_TEST_FOO")) == Str("bar")
    Environ.unset(Str("POOP_TEST_FOO"))
    assert Environ.has(Str("POOP_TEST_FOO")) is false


def test_environ_get_default() -> None:
    assert Environ.get(Str("POOP_MISSING_KEY"), Str("fallback")) == Str("fallback")


def test_environ_get_missing_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POOP_MISSING_KEY", raising=False)
    assert Environ.get(Str("POOP_MISSING_KEY")) is none


def test_environ_keys_returns_set() -> None:
    assert isinstance(Environ.keys(), Set)


def test_environ_values_returns_list() -> None:
    assert isinstance(Environ.values(), List)


def test_environ_as_dict_returns_dict() -> None:
    assert isinstance(Environ.as_dict(), Dict)


def test_environ_unset_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POOP_NEVER_SET", raising=False)
    assert Environ.unset(Str("POOP_NEVER_SET")) is none


def test_environ_reachable_via_os_attr() -> None:
    # Both spellings resolve to the same namespace.
    assert OS.environ.has is Environ.has


# --- Interpreter integration ---


def test_os_via_interpreter() -> None:
    Interpreter().run_source("os.cpu_count().print()")


def test_os_pid_via_interpreter() -> None:
    Interpreter().run_source("os.getpid().print()")


def test_environ_via_interpreter() -> None:
    Interpreter().run_source("os.environ.has('PATH').print()")


# --- os.walk ---


def test_walk_yields_tuples_of_path_dirs_files(tmp_path: _PyPath) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "file.txt").write_text("x")
    result = OS.walk(Path(Str(str(tmp_path))))
    assert isinstance(result, List)
    first = result.at(Int(0))
    assert isinstance(first, Tuple)
    root, dirs, files = first.at(Int(0)), first.at(Int(1)), first.at(Int(2))
    assert isinstance(root, Path)
    assert isinstance(dirs, List)
    assert isinstance(files, List)


def test_walk_topdown_false() -> None:
    # Just verifying the kwarg threads through without raising.
    result = OS.walk(Path(Str(".")), topdown=false)
    assert isinstance(result, List)


def test_walk_onerror_block_receives_oserror(tmp_path: _PyPath) -> None:
    seen: list[OSError] = []

    def handler(err: OSError) -> None:
        seen.append(err)

    # Walk a nonexistent dir under followlinks=false; onerror fires on
    # the listdir failure.
    OS.walk(
        Path(Str(str(tmp_path / "nonexistent"))),
        onerror=Block(handler),
    )
    assert seen and isinstance(seen[0], OSError)
