import ast

import pytest

from poop.transformers.int import IntTransformer, _poop_int_from
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return IntTransformer().transform(tree)


def test_int_literal_is_rewritten() -> None:
    tree = _transform("x = 42")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_int"
    assert isinstance(call.args[0], ast.Constant)
    assert call.args[0].value == 42


def test_bool_literal_is_not_rewritten() -> None:
    tree = _transform("x = True")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Constant)
    assert assign.value.value is True


def test_string_literal_is_not_rewritten() -> None:
    tree = _transform('x = "hello"')
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Constant)


def test_negative_int_literal_is_collapsed() -> None:
    tree = _transform("x = -1")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_int"
    assert isinstance(call.args[0], ast.Constant)
    assert call.args[0].value == -1


def test_bindings_contains_int_class() -> None:
    assert IntTransformer.BINDINGS["_poop_int"] is Int


def test_bindings_contains_int_from_factory() -> None:
    assert IntTransformer.BINDINGS["_poop_int_from"] is _poop_int_from


def test_int_call_is_rewritten() -> None:
    tree = _transform('int("42")')
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_int_from"


def test_int_call_with_base_is_rewritten() -> None:
    tree = _transform('int("ff", 16)')
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_int_from"
    assert len(expr.value.args) == 2


def test_method_named_int_is_not_rewritten() -> None:
    tree = _transform("x.int()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "int"


# _poop_int_from factory tests


def test_int_from_int_returns_same() -> None:
    x = Int(42)
    assert _poop_int_from(x) is x


def test_int_from_none_returns_zero() -> None:
    result = _poop_int_from()
    assert isinstance(result, Int)
    assert result._value == 0


def test_int_from_float_truncates() -> None:
    result = _poop_int_from(Float(3.9))
    assert isinstance(result, Int)
    assert result._value == 3


def test_int_from_str_parses() -> None:
    result = _poop_int_from(Str("42"))
    assert isinstance(result, Int)
    assert result._value == 42


def test_int_from_str_with_base() -> None:
    result = _poop_int_from(Str("ff"), Int(16))
    assert isinstance(result, Int)
    assert result._value == 255


def test_int_from_str_with_non_int_base_raises() -> None:
    with pytest.raises(TypeError, match="base must be Int"):
        _poop_int_from(Str("10"), "invalid_base")


def test_int_from_non_string_with_base_raises() -> None:
    # CPython: int(10, 2) / int(3.5, 2) / int(True, 2) raise
    # "int() can't convert non-string with explicit base". The base must
    # not be silently dropped for Int/Float/Boolean values.
    from poop.types.boolean import true

    for value in (Int(10), Float(3.5), true):
        with pytest.raises(
            TypeError, match="can't convert non-string with explicit base"
        ):
            _poop_int_from(value, Int(2))


def test_int_from_boolean() -> None:
    # proposal 154: int(True) -> 1, int(False) -> 0.
    from poop.types.boolean import false, true

    assert _poop_int_from(true) == Int(1)
    assert _poop_int_from(false) == Int(0)


def test_int_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_int_from(Complex(complex(1, 2)))


def test_int_from_error_uses_masked_name() -> None:
    # The diagnostic must show the public name, not internal class names.
    with pytest.raises(TypeError, match="cannot convert complex to Int"):
        _poop_int_from(Complex(complex(1, 2)))


def test_negative_variable_not_collapsed() -> None:
    tree = _transform("x = -y")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.UnaryOp)
