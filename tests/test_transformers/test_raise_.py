import ast

import pytest

from poop.transformers.raise_ import RaiseTransformer, _poop_raise


def _first_expr(source: str) -> ast.expr:
    tree = ast.parse(source)
    transformed = RaiseTransformer().transform(tree)
    stmt = transformed.body[0]
    assert isinstance(stmt, ast.Expr)
    return stmt.value


def test_uppercase_raise_rewritten_to_poop_raise() -> None:
    value = _first_expr("KeyError.raise_('msg')")
    assert isinstance(value, ast.Call)
    assert isinstance(value.func, ast.Name)
    assert value.func.id == "_poop_raise"


def test_rewritten_call_has_exc_type_as_first_arg() -> None:
    value = _first_expr("ValueError.raise_('oops')")
    assert isinstance(value, ast.Call)
    args = value.args
    assert isinstance(args[0], ast.Name)
    assert args[0].id == "ValueError"


def test_rewritten_call_passes_message_as_second_arg() -> None:
    value = _first_expr("RuntimeError.raise_('boom')")
    assert isinstance(value, ast.Call)
    assert isinstance(value.args[1], ast.Constant)
    assert value.args[1].value == "boom"


def test_lowercase_receiver_not_rewritten() -> None:
    value = _first_expr("my_error.raise_()")
    assert isinstance(value, ast.Call)
    assert isinstance(value.func, ast.Attribute)
    assert value.func.attr == "raise_"


def test_non_raise_method_not_rewritten() -> None:
    value = _first_expr("KeyError.something('msg')")
    assert isinstance(value, ast.Call)
    assert isinstance(value.func, ast.Attribute)
    assert value.func.attr == "something"


def test_transformed_nodes_have_line_info() -> None:
    tree = ast.parse("KeyError.raise_('msg')")
    transformed = RaiseTransformer().transform(tree)
    stmt = transformed.body[0]
    assert isinstance(stmt, ast.Expr)
    assert hasattr(stmt.value, "lineno")


def test_bindings_contain_poop_raise() -> None:
    assert "_poop_raise" in RaiseTransformer.BINDINGS
    assert RaiseTransformer.BINDINGS["_poop_raise"] is _poop_raise


def test_poop_raise_raises_given_exception_type() -> None:
    with pytest.raises(KeyError, match="missing"):
        _poop_raise(KeyError, "missing")


def test_poop_raise_with_no_message() -> None:
    with pytest.raises(RuntimeError):
        _poop_raise(RuntimeError)
