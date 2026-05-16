import os

from poop.interpreter import Interpreter
from poop.types.int import Int
from poop.types.list import List
from poop.types.pwd import Passwd, Pwd
from poop.types.string import Str


def _current_uid() -> int:
    return os.getuid()


def test_getpwuid_returns_passwd() -> None:
    entry = Pwd.getpwuid(Int(_current_uid()))
    assert isinstance(entry, Passwd)
    assert entry.pw_uid == Int(_current_uid())


def test_passwd_properties() -> None:
    entry = Pwd.getpwuid(Int(_current_uid()))
    assert isinstance(entry.pw_name, Str)
    assert isinstance(entry.pw_passwd, Str)
    assert isinstance(entry.pw_uid, Int)
    assert isinstance(entry.pw_gid, Int)
    assert isinstance(entry.pw_gecos, Str)
    assert isinstance(entry.pw_dir, Str)
    assert isinstance(entry.pw_shell, Str)


def test_getpwnam_round_trips_with_getpwuid() -> None:
    by_uid = Pwd.getpwuid(Int(_current_uid()))
    by_name = Pwd.getpwnam(by_uid.pw_name)
    assert by_name.pw_uid == by_uid.pw_uid


def test_getpwall_returns_list() -> None:
    result = Pwd.getpwall()
    assert isinstance(result, List)
    # At least the root account is present on every Unix system.
    assert result.len()._value > 0


def test_passwd_repr() -> None:
    entry = Pwd.getpwuid(Int(_current_uid()))
    assert repr(entry).startswith("pwd.struct_passwd")


def test_pwd_class_ref() -> None:
    assert Pwd.Passwd is Passwd


# --- Interpreter integration ---


def test_pwd_via_interpreter() -> None:
    Interpreter().run_source(f"pwd.getpwuid({_current_uid()}).pw_name.print()")
