import pytest

from poop.errors import (
    ExecutionError,
    ExitCode,
    ParseError,
    PoopError,
    TransformError,
    ValidationError,
)
from poop.types.exceptions import describe_chain


def test_describe_chain_follows_the_cause_then_the_unsuppressed_context() -> None:
    first, second, third = ValueError("a"), KeyError("b"), IndexError("c")
    third.__cause__ = second
    second.__context__ = first
    assert describe_chain(third) == [
        "caused by KeyError: 'b'",
        "while handling ValueError: a",
    ]


def test_describe_chain_stops_at_a_suppressed_context() -> None:
    outer, inner = KeyError("b"), ValueError("a")
    outer.__context__ = inner
    outer.__suppress_context__ = True
    assert describe_chain(outer) == []


def test_describe_chain_stops_at_a_cycle() -> None:
    # A handler can link two exceptions to each other; the walk must end.
    a, b = ValueError("a"), KeyError("b")
    a.__cause__, b.__cause__ = b, a
    assert describe_chain(a) == ["caused by KeyError: 'b'"]


@pytest.mark.parametrize(
    ("kind", "code"),
    [
        (ParseError, ExitCode.NOT_A_PROGRAM),
        (ValidationError, ExitCode.REFUSED),
        (TransformError, ExitCode.FAILED),
        (ExecutionError, ExitCode.FAILED),
    ],
    ids=["parse", "validation", "transform", "execution"],
)
def test_an_error_and_its_subclass_carry_the_same_exit_code(
    kind: type[PoopError], code: ExitCode
) -> None:
    sub = type("Sub", (kind,), {})
    assert kind.exit_code == code
    assert sub.exit_code == code


def test_an_error_of_no_kind_exits_as_a_failure() -> None:
    assert PoopError("x").exit_code == ExitCode.FAILED
