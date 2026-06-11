import pytest

from poop.interpreter import Interpreter
from poop.types.enum import (
    Enum,
    EnumNamespace,
    Flag,
    IntEnum,
    IntFlag,
    StrEnum,
    auto,
)
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple

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


# Functional API (proposal 124)


def test_functional_api_list_of_names() -> None:
    made = Enum("Mades1", List(Str("RED"), Str("GREEN")))
    assert made.RED.value_object() == Int(1)  # ty: ignore[unresolved-attribute]
    assert made.GREEN.value_object() == Int(2)  # ty: ignore[unresolved-attribute]


def test_functional_api_space_separated_str() -> None:
    made = Enum("Mades2", Str("RED GREEN BLUE"))
    assert made.BLUE.value_object() == Int(3)  # ty: ignore[unresolved-attribute]


def test_functional_api_name_value_pairs() -> None:
    made = Enum(
        "Mades3",
        List(Tuple(Str("RED"), Int(10)), Tuple(Str("GREEN"), Int(20))),
    )
    assert made.GREEN.value_object() == Int(20)  # ty: ignore[unresolved-attribute]


def test_functional_api_int_enum() -> None:
    from poop.types.boolean import true

    made = IntEnum("Mades4", List(Str("A"), Str("B"), Str("C")))
    assert (made.A < made.C) is true  # ty: ignore[unresolved-attribute]


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


# --- Operator bridging (proposal 144) ---


def test_enum_eq_returns_poop_boolean() -> None:
    from poop.types.boolean import Boolean, false, true

    assert isinstance(Color.RED == Color.RED, Boolean)
    assert (Color.RED == Color.RED) is true
    assert (Color.RED == Color.GREEN) is false
    assert (Color.RED != Color.GREEN) is true


def test_enum_eq_enables_dispatch_via_interpreter() -> None:
    Interpreter().run_source(
        "class State(Enum):\n"
        "    IDLE = 1\n"
        "    BUSY = 2\n"
        "(State.IDLE == State.IDLE).if_true(lambda: 'idle'.print())"
    )


def test_int_enum_ordering_returns_boolean() -> None:
    from poop.types.boolean import Boolean, true

    assert isinstance(HTTPStatus.OK < HTTPStatus.NOT_FOUND, Boolean)
    assert (HTTPStatus.OK < HTTPStatus.NOT_FOUND) is true
    assert (HTTPStatus.NOT_FOUND >= HTTPStatus.OK) is true


def test_int_enum_arithmetic_returns_poop_int() -> None:
    result = HTTPStatus.OK + HTTPStatus.OK
    assert isinstance(result, Int)
    assert result == Int(400)


def test_enum_hash_keeps_member_dict_lookup() -> None:
    # The override must not break hash-based member identity.
    seen = {Color.RED: Str("r"), Color.GREEN: Str("g")}
    assert seen[Color.RED] == Str("r")


def test_enum_alias_resolution_survives_eq_override() -> None:
    class Named(Enum):
        RED = 1
        CRIMSON = 1

    assert Named.CRIMSON is Named.RED


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


# --- auto() value wrapping (proposal 162) ---


class _AutoColor(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()


def test_enum_auto_value_is_poop_int() -> None:
    # The leak: .value used to answer a raw int and crash on .print().
    assert isinstance(_AutoColor.RED.value, Int)
    assert _AutoColor.RED.value == Int(1)


def test_enum_auto_increments() -> None:
    assert _AutoColor.GREEN.value == Int(2)
    assert _AutoColor.BLUE.value == Int(3)


def test_enum_auto_lookup_by_poop_int() -> None:
    assert _AutoColor(Int(1)) is _AutoColor.RED


def test_enum_auto_via_interpreter_value_prints() -> None:
    # End-to-end: a literal member and an auto() member behave the same.
    Interpreter().run_source(
        "class Color(Enum):\n    RED = 1\n    GREEN = auto()\nColor.GREEN.value.print()"
    )


class _AutoFlag(Flag):
    READ = auto()
    WRITE = auto()
    EXEC = auto()


def test_flag_auto_keeps_combination() -> None:
    # Flag values stay raw so the mask/combination machinery keeps working.
    assert (_AutoFlag.READ | _AutoFlag.EXEC).value_object() == Int(5)


class _AutoSize(StrEnum):
    SMALL = auto()
    LARGE = auto()


def test_str_enum_auto_lowercases_name() -> None:
    assert _AutoSize.SMALL.value_object() == Str("small")


class _AutoPrio(IntEnum):
    LOW = auto()
    HIGH = auto()


def test_int_enum_auto_value_object() -> None:
    assert _AutoPrio.HIGH.value_object() == Int(2)
