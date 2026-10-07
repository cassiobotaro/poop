import ast
from functools import partial

import pytest

from poop.interpreter import Interpreter
from poop.transformers.unpack import UnpackTransformer, _rebind
from tests._support import rewritten

_rewritten = partial(rewritten, UnpackTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("c, *rest = xs", "c, *rest = xs\nrest = _poop_list_from(rest)"),
        ("a, b = xs", "a, b = xs"),
        ("a, (b, *inner) = xs", "a, (b, *inner) = xs\ninner = _poop_list_from(inner)"),
        (
            "a, *self.rest = xs",
            "a, *self.rest = xs\nself.rest = _poop_list_from(self.rest)",
        ),
    ],
    ids=[
        "starred_assign_appends_rebind",
        "plain_assign_unchanged",
        "nested_starred_rebinds_inner",
        "attribute_starred_target",
    ],
)
def test_unpack_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_rest_is_poop_list_via_interpreter() -> None:
    Interpreter().run_source("c, *rest = [1, 2, 3]\nrest.class_name().print()")


def test_rest_from_tuple_via_interpreter() -> None:
    Interpreter().run_source("a, *b = (1, 2, 3)\nb.len().print()")


def test_rest_from_str_via_interpreter() -> None:
    Interpreter().run_source("first, *others = 'xyz'\nothers.len().print()")


def test_rebind_tolerates_a_target_without_ctx() -> None:
    # A rest-target is always a ctx-carrying assignable in practice; the guard
    # still degrades gracefully if handed a node type that carries no ctx.
    assign = _rebind(ast.Constant(value=1))
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Call)
