import pytest

from poop.interpreter import Interpreter
from poop.types.enum import (
    Enum,
    EnumNamespace,
    IntEnum,
    IntFlag,
    StrEnum,
    auto,
)
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str

# --- Basic Enum ---


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


def test_enum_member_access_by_attribute() -> None:
    # .value returns whatever was assigned — raw int here.
    assert Color.RED.value == 1


def test_enum_name_str_returns_poop_str() -> None:
    # .name stays Python str (Python's enum protocol relies on it);
    # use .name_str() for POOP Str.
    assert Color.RED.name == "RED"
    assert Color.RED.name_str() == Str("RED")
    assert isinstance(Color.RED.name_str(), Str)


def test_enum_value_object_returns_int() -> None:
    # .value_object() wraps the raw value to a POOP type.
    assert Color.RED.value_object() == Int(1)
    assert isinstance(Color.RED.value_object(), Int)


def test_enum_lookup_by_raw_value() -> None:
    assert Color(1) is Color.RED


def test_enum_lookup_by_poop_int() -> None:
    assert Color(Int(2)) is Color.GREEN


def test_enum_iter_returns_list() -> None:
    members = Color.iter()
    assert isinstance(members, List)
    assert members.len() == Int(3)


def test_enum_unknown_value_raises() -> None:
    with pytest.raises(ValueError):
        Color(99)


# --- IntEnum ---


class HTTPStatus(IntEnum):
    OK = 200
    NOT_FOUND = 404


def test_int_enum_value_is_int() -> None:
    assert HTTPStatus.OK.value_object() == Int(200)


def test_int_enum_compares_to_int() -> None:
    # IntEnum members ARE ints.
    assert HTTPStatus.OK == 200


def test_int_enum_lookup_by_poop_int() -> None:
    assert HTTPStatus(Int(404)) is HTTPStatus.NOT_FOUND


# --- StrEnum ---


class Mode(StrEnum):
    READ = "r"
    WRITE = "w"


def test_str_enum_value_is_str() -> None:
    assert Mode.READ.value_object() == Str("r")


def test_str_enum_lookup_by_poop_str() -> None:
    assert Mode(Str("w")) is Mode.WRITE


# --- Flag / IntFlag ---


class Permission(IntFlag):
    READ = 1
    WRITE = 2
    EXECUTE = 4


def test_int_flag_combines_bitwise() -> None:
    combined = Permission.READ | Permission.WRITE
    assert combined.value_object() == Int(3)


def test_int_flag_iter() -> None:
    members = Permission.iter()
    assert isinstance(members, List)


# --- auto() ---


class Stage(Enum):
    INIT = auto()
    RUNNING = auto()
    DONE = auto()


def test_auto_assigns_sequential_int() -> None:
    assert Stage.INIT.value_object() == Int(1)
    assert Stage.RUNNING.value_object() == Int(2)
    assert Stage.DONE.value_object() == Int(3)


# --- Decorators ---


def test_unique_accepts_unique_enum() -> None:
    @EnumNamespace.unique
    class Letter(Enum):
        A = 1
        B = 2

    assert Letter.A.value_object() == Int(1)


def test_unique_rejects_aliases() -> None:
    with pytest.raises(ValueError):

        @EnumNamespace.unique
        class WithAlias(Enum):
            A = 1
            ALIAS_OF_A = 1


# --- Interpreter integration ---


def test_enum_reachable_via_interpreter() -> None:
    src = (
        "class Status(Enum):\n"
        "    ACTIVE = 1\n"
        "    INACTIVE = 2\n"
        "Status.ACTIVE.name_str().print()\n"
        "Status.ACTIVE.value_object().print()\n"
    )
    Interpreter().run_source(src)


def test_enum_lookup_reachable_via_interpreter() -> None:
    src = (
        "class Status(Enum):\n"
        "    ACTIVE = 1\n"
        "    INACTIVE = 2\n"
        "Status(2).name_str().print()\n"
    )
    Interpreter().run_source(src)


def test_auto_reachable_via_interpreter() -> None:
    src = (
        "class Phase(Enum):\n"
        "    START = auto()\n"
        "    END = auto()\n"
        "Phase.END.value_object().print()\n"
    )
    Interpreter().run_source(src)
