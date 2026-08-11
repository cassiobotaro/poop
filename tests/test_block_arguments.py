"""Every message that takes a block says so when it is handed something else.

`_require_block` was written for one sentence, quoted in its own docstring:
CPython answers `'int' object is not callable`, which is "true of every POOP
object, and silent about what was expected". `Try` and `With` routed their four
block arguments through it. Every other message that takes a block reached the
deferred call instead, and the language has about forty of them.

Sending a non-block split three ways, and all three were wrong:

- seventeen leaked CPython's sentence;
- five **accepted in silence**, because `map`, `filter` and `filter_false`
  answer a view and call nothing until it is walked — so the failure surfaced
  somewhere else entirely, or never;
- the rest reported or not depending on the *receiver's value*:
  `True.if_true(5)` refused while `True.if_false(5)` said nothing, and `False`
  swapped them. A program could ship a mistake that only reports on the branch
  it does not usually take.

The enumeration below is derived from the signatures, so a new block-taking
message cannot ship unguarded: `ast` walks `poop/types/` for every parameter
annotated `Callable`, and each one is sent an `Int`.
"""

import ast
import pathlib

import pytest

from poop.errors import ExecutionError, PoopError
from poop.interpreter import Interpreter

_TYPES = pathlib.Path(__file__).parent.parent / "poop" / "types"

# The sentence every block guard composes. `Try` and `With` keep
# `_require_block`'s original role-first wording (`the handler must be a
# block`), which reads better where the argument has a name of its own.
_SAYS_BLOCK = ("expects a block", "must be a block")


def _callable_parameters() -> set[tuple[str, str]]:
    """(module, message) for every public message taking a `Callable`."""
    found: set[tuple[str, str]] = set()
    for path in sorted(_TYPES.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            args = node.args
            params = [*args.posonlyargs, *args.args, *args.kwonlyargs]
            for param in params:
                if param.annotation is None:
                    continue
                if "Callable" in ast.unparse(param.annotation):
                    found.add((path.name, node.name))
    return found


def test_the_enumeration_is_not_empty() -> None:
    # A silent zero here would make every assertion below vacuous.
    assert len(_callable_parameters()) >= 25


# One reachable program per message, since a signature alone cannot say what
# receiver to send it to. Every entry hands the message an `Int` where a block
# belongs.
_PROGRAMS = [
    "[1, 2].do(5)",
    "[1, 2].map(5)",
    "[1, 2].filter(5)",
    "[1, 2].filter_false(5)",
    "[1, 2].find(5)",
    "[1, 2].reduce(0, 5)",
    "[1, 2].all(5)",
    "[1, 2].any(5)",
    "[1, 2].sorted(key=5)",
    "[1, 2].sort(key=5)",
    "[1, 2].min(key=5)",
    "[1, 2].max(key=5)",
    "(1, 2).sorted(key=5)",
    '{"a": 1}.min(key=5)',
    '"ab".min(key=5)',
    "(5).max(6, key=5)",
    "(2.5).max(6.0, key=5)",
    '{"a": 1}.iter().do(5)',
    "True.if_true(5)",
    "True.if_false(5)",
    "False.if_true(5)",
    "False.if_false(5)",
    "True.and_(5)",
    "True.or_(5)",
    "False.and_(5)",
    "False.or_(5)",
    "True.if_true_if_false(lambda: 1, 5)",
    "True.if_true_if_false(5, lambda: 1)",
    "False.if_true_if_false(lambda: 1, 5)",
    "False.if_true_if_false(5, lambda: 1)",
    "True.if_false_if_true(5, lambda: 1)",
    "False.if_false_if_true(lambda: 1, 5)",
    "(5).if_none(5)",
    "(5).if_not_none(5)",
    "None.if_none(5)",
    "None.if_not_none(5)",
    "int.if_none(5)",
    "int.if_not_none(5)",
    "(lambda: 1).while_true(5)",
    "(lambda: 1).while_false(5)",
    "Try(5).run()",
    "Try(lambda: 1).except_(Exception, 5)",
    "Try(lambda: 1).finally_(5)",
    "With(5).do(lambda x: x)",
    "With(lambda: 5).do(5)",
]


@pytest.mark.parametrize("source", _PROGRAMS)
def test_a_non_block_is_refused_by_the_message_that_wanted_one(source: str) -> None:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source + "\n")
    message = str(info.value)
    assert any(phrase in message for phrase in _SAYS_BLOCK), (
        f"{source!r} answered {message!r}"
    )
    # The sentence `_require_block` was written to remove.
    assert "not callable" not in message


@pytest.mark.parametrize(
    "source",
    ["[1, 2].map(5)", "[1, 2].filter(5)", "[1, 2].filter_false(5)"],
)
def test_a_lazy_view_refuses_before_it_is_walked(source: str) -> None:
    # The half no wording change reaches: these answer a view and call nothing,
    # so an unguarded `Map` simply failed later — or never. The refusal has to
    # land at the call the reader wrote.
    with pytest.raises(ExecutionError, match="expects a block"):
        Interpreter().run_source(source + "\n")


@pytest.mark.parametrize(
    ("receiver", "selector"),
    [
        ("True", "if_true"),
        ("True", "if_false"),
        ("False", "if_true"),
        ("False", "if_false"),
        ("True", "and_"),
        ("True", "or_"),
        ("False", "and_"),
        ("False", "or_"),
    ],
)
def test_a_branch_refuses_whichever_way_the_receiver_falls(
    receiver: str, selector: str
) -> None:
    # The sharpest half: whether a wrong argument was reported at all depended
    # on the receiver's *value*. `and_` refused and `or_` did not, on the same
    # receiver; `False` swapped `if_true` and `if_false`.
    with pytest.raises(ExecutionError, match="expects a block"):
        Interpreter().run_source(f"{receiver}.{selector}(5)\n")


def test_a_real_block_still_works_everywhere() -> None:
    Interpreter().run_source(
        "[1, 2].map(lambda x: x + 1).do(lambda x: x)\n"
        "[3, 1].sorted(key=lambda x: x).print()\n"
        "True.if_true(lambda: 1).print()\n"
        "True.if_true_if_false(lambda: 1, lambda: 2).print()\n"
        "(5).if_not_none(lambda v: v).print()\n"
        "None.if_none(lambda: 9).print()\n"
        "[1, 2].reduce(0, lambda a, b: a + b).print()\n"
    )


def test_an_absent_key_is_still_absent() -> None:
    # `key` is the one block slot that is optional, which is why it cannot go
    # through `a_block`: absence has to reach `sorted` as "no key at all".
    Interpreter().run_source(
        "[3, 1].sorted().print()\n"
        "[3, 1].sorted(key=None).print()\n"
        "[3, 1].min().print()\n"
    )


# Proposal 46. A missing block fell through to CPython's call machinery, which
# builds its sentence from the *function's* qualname — and the mixins are
# cloaked as `object`, since no single builtin name is true for every wrapper
# that inherits them. So `[1, 2].map()` blamed `object.map()`: a name a program
# can write, for a class that does not answer `#map`, checkable in one line and
# the opposite of what the refusal had just said.
@pytest.mark.parametrize(
    "source",
    [
        "[1, 2].do()",
        "[1, 2].map()",
        "[1, 2].filter()",
        "[1, 2].filter_false()",
        "[1, 2].find()",
        "[1, 2].all()",
        "[1, 2].any()",
        '"ab".do()',
        '{"a": 1}.map()',
        "(1, 2).find()",
    ],
)
def test_a_missing_block_is_refused_by_the_receiver(source: str) -> None:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source + "\n")
    message = str(info.value)
    assert "expects a block, got nothing" in message
    # The falsifiable half: `object` does not answer any of these.
    assert "object." not in message
    assert "positional argument" not in message


def test_reduce_names_the_initial_value_it_is_missing() -> None:
    with pytest.raises(PoopError, match="expects an initial value and a block"):
        Interpreter().run_source("[1, 2].reduce()\n")
    with pytest.raises(PoopError, match="#reduce expects a block, got nothing"):
        Interpreter().run_source("[1, 2].reduce(0)\n")
