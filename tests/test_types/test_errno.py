import errno as _errno

from poop.interpreter import Interpreter
from poop.types.dict import Dict
from poop.types.errno import Errno
from poop.types.int import Int
from poop.types.string import Str


def test_eperm_is_poop_int() -> None:
    assert isinstance(Errno.EPERM, Int)
    assert Errno.EPERM._value == _errno.EPERM


def test_enoent_is_poop_int() -> None:
    assert isinstance(Errno.ENOENT, Int)
    assert Errno.ENOENT._value == _errno.ENOENT


def test_eagain_alias_is_ewouldblock() -> None:
    # On Linux EAGAIN and EWOULDBLOCK share the same numeric code.
    assert Errno.EAGAIN._value == Errno.EWOULDBLOCK._value


def test_errorcode_is_dict() -> None:
    assert isinstance(Errno.errorcode, Dict)


def test_errorcode_maps_int_to_str() -> None:
    name = Errno.errorcode.at(Int(_errno.EPERM))
    assert isinstance(name, Str)
    assert name._value == "EPERM"


def test_errorcode_size_matches_cpython() -> None:
    assert Errno.errorcode.len()._value == len(_errno.errorcode)


def test_every_cpython_code_is_exposed() -> None:
    for name in dir(_errno):
        if name.startswith("_") or name == "errorcode":
            continue
        value = getattr(_errno, name)
        if isinstance(value, int):
            attr = getattr(Errno, name)
            assert isinstance(attr, Int)
            assert attr._value == value


def test_errno_reachable_via_interpreter() -> None:
    Interpreter().run_source("errno.EPERM.print()")


def test_errno_errorcode_reachable_via_interpreter() -> None:
    Interpreter().run_source("errno.errorcode.at(errno.EPERM).print()")
