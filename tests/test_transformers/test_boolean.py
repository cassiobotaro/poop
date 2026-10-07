import ast
from functools import partial

import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter
from poop.transformers.boolean import BooleanTransformer, _poop_bool_from
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, BooleanTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = True", "x = _poop_true"),
        ("x = False", "x = _poop_false"),
        ("bool(x)", "_poop_bool_from(x)"),
    ],
    ids=["true_literal", "false_literal", "call"],
)
def test_bool_is_rewritten(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


@pytest.mark.parametrize(
    "source",
    ["x = 1", "x = 'hello'", "x.bool()"],
    ids=["int_constant", "str_constant", "method_named_bool"],
)
def test_bool_is_not_rewritten(source: str) -> None:
    assert _rewritten(source) == source


def test_transformed_nodes_have_line_info() -> None:
    tree = ast.parse("x = True")
    transformed = BooleanTransformer().transform(tree)
    assign = transformed.body[0]
    assert isinstance(assign, ast.Assign)
    name_node = assign.value
    assert hasattr(name_node, "lineno")
    assert name_node.lineno == 1


def test_bindings_contain_true_and_false_singletons() -> None:
    bindings = BooleanTransformer.BINDINGS
    assert bindings["_poop_true"] is true
    assert bindings["_poop_false"] is false


def test_bindings_contain_bool_from_factory() -> None:
    assert BooleanTransformer.BINDINGS["_poop_bool_from"] is _poop_bool_from


# _poop_bool_from factory tests


def test_bool_from_no_arg_returns_false() -> None:
    assert _poop_bool_from() is false


def test_bool_from_true_singleton_returns_same() -> None:
    assert _poop_bool_from(true) is true


def test_bool_from_false_singleton_returns_same() -> None:
    assert _poop_bool_from(false) is false


def test_bool_from_truthy_value_returns_true() -> None:
    assert _poop_bool_from(Int(1)) is true


def test_bool_from_falsy_value_returns_false() -> None:
    assert _poop_bool_from(Int(0)) is false


def test_bool_from_nonempty_str_returns_true() -> None:
    assert _poop_bool_from(Str("hello")) is true


def test_bool_from_empty_str_returns_false() -> None:
    assert _poop_bool_from(Str("")) is false


def test_bool_refuses_a_keyword_argument() -> None:
    # The helper's argument is optional, so a rewritten `bool(x=1)` fell
    # through to the default and answered `False` where CPython raises. The
    # guard declines to rewrite, leaving the callee to refuse the keyword the
    # way `str(x=1)` and `list(x=1)` already do.
    with pytest.raises(ExecutionError, match="bool"):
        Interpreter().run_source("bool(x=1).print()")
