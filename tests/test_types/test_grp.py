import os

from poop.interpreter import Interpreter
from poop.types.grp import Group, Grp
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def _current_gid() -> int:
    return os.getgid()


def test_getgrgid_returns_group() -> None:
    entry = Grp.getgrgid(Int(_current_gid()))
    assert isinstance(entry, Group)
    assert entry.gr_gid == Int(_current_gid())


def test_group_properties() -> None:
    entry = Grp.getgrgid(Int(_current_gid()))
    assert isinstance(entry.gr_name, Str)
    assert isinstance(entry.gr_passwd, Str)
    assert isinstance(entry.gr_gid, Int)
    assert isinstance(entry.gr_mem, List)


def test_getgrnam_round_trips_with_getgrgid() -> None:
    by_gid = Grp.getgrgid(Int(_current_gid()))
    by_name = Grp.getgrnam(by_gid.gr_name)
    assert by_name.gr_gid == by_gid.gr_gid


def test_getgrall_returns_list() -> None:
    result = Grp.getgrall()
    assert isinstance(result, List)
    assert result.len()._value > 0


def test_group_repr() -> None:
    entry = Grp.getgrgid(Int(_current_gid()))
    assert repr(entry).startswith("grp.struct_group")


def test_grp_class_ref() -> None:
    assert Grp.Group is Group


# --- Interpreter integration ---


def test_grp_via_interpreter() -> None:
    Interpreter().run_source(f"grp.getgrgid({_current_gid()}).gr_name.print()")
