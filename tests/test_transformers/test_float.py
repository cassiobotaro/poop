import ast

import pytest

from poop.transformers.float import FloatTransformer, _poop_float_from
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


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
    assert result._value == pytest.approx(0.0)


def test_float_from_int_converts() -> None:
    result = _poop_float_from(Int(42))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(42.0)


def test_float_from_str_parses() -> None:
    result = _poop_float_from(Str("3.14"))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.14)


def test_float_from_boolean() -> None:
    # proposal 154: float(True) -> 1.0, float(False) -> 0.0.
    from poop.types.boolean import false, true

    assert _poop_float_from(true) == Float(1.0)
    assert _poop_float_from(false) == Float(0.0)


def test_float_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert complex to float"):
        _poop_float_from(Complex(complex(1, 2)))


def test_negative_variable_not_collapsed() -> None:
    tree = _transform("x = -y")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.UnaryOp)


def test_negative_non_float_literal_is_not_wrapped_as_a_float() -> None:
    # `-5` is USub on a Constant, but the value is an int, not a float, so the
    # float rewriter leaves it for the int transformer instead of wrapping it.
    tree = _transform("y = -5")
    assert "_poop_float" not in ast.unparse(tree)


def test_float_from_an_unparsable_string_names_the_value() -> None:
    # `could not convert string to float: 'abc'` names Python's type, not the
    # message the reader sent.
    with pytest.raises(ValueError, match=r"^'abc' is not a valid float$"):
        _poop_float_from(Str("abc"))
