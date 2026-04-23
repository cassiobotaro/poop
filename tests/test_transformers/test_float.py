import ast

import pytest

from poop.transformers.float import FloatTransformer, _poop_float_from
from poop.types.float import Float


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return FloatTransformer().transform(tree)


def test_float_literal_is_rewritten() -> None:
    tree = _transform("x = 3.14")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_float"
    assert isinstance(call.args[0], ast.Constant)
    assert call.args[0].value == 3.14


def test_int_literal_is_not_rewritten() -> None:
    tree = _transform("x = 42")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Constant)


def test_string_literal_is_not_rewritten() -> None:
    tree = _transform('x = "hello"')
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Constant)


def test_negative_float_literal_is_collapsed() -> None:
    tree = _transform("x = -3.14")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_float"
    assert isinstance(call.args[0], ast.Constant)
    assert call.args[0].value == -3.14


def test_bindings_contains_float_class() -> None:
    assert FloatTransformer.BINDINGS["_poop_float"] is Float


def test_bindings_contains_float_from_factory() -> None:
    assert FloatTransformer.BINDINGS["_poop_float_from"] is _poop_float_from


def test_float_call_is_rewritten() -> None:
    tree = _transform('float("3.14")')
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_float_from"


def test_method_named_float_is_not_rewritten() -> None:
    tree = _transform("x.float()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "float"


# _poop_float_from factory tests


def test_float_from_float_returns_same() -> None:
    x = Float(3.14)
    assert _poop_float_from(x) is x


def test_float_from_none_returns_zero() -> None:
    result = _poop_float_from()
    assert isinstance(result, Float)
    assert result._value == 0.0


def test_float_from_int_converts() -> None:
    from poop.types.int import Int

    result = _poop_float_from(Int(42))
    assert isinstance(result, Float)
    assert result._value == 42.0


def test_float_from_str_parses() -> None:
    from poop.types.string import Str

    result = _poop_float_from(Str("3.14"))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.14)
