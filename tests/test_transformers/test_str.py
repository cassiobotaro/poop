import ast

from poop.transformers.string import StrTransformer, _poop_str_from
from poop.types.string import Str


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return StrTransformer().transform(tree)


def test_str_literal_is_rewritten() -> None:
    tree = _transform('x = "hello"')
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_str"
    assert isinstance(call.args[0], ast.Constant)
    assert call.args[0].value == "hello"


def test_int_literal_is_not_rewritten() -> None:
    tree = _transform("x = 42")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Constant)
    assert assign.value.value == 42


def test_bindings_contains_str_class() -> None:
    assert StrTransformer.BINDINGS["_poop_str"] is Str


def test_bindings_contains_str_from_factory() -> None:
    assert StrTransformer.BINDINGS["_poop_str_from"] is _poop_str_from


def test_str_call_is_rewritten() -> None:
    tree = _transform("str(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_str_from"


def test_method_named_str_is_not_rewritten() -> None:
    tree = _transform("x.str()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "str"


# _poop_str_from factory tests


def test_str_from_no_arg_returns_empty_str() -> None:
    result = _poop_str_from()
    assert isinstance(result, Str)
    assert result._value == ""


def test_str_from_str_returns_same() -> None:
    x = Str("hello")
    assert _poop_str_from(x) is x


def test_str_from_int_converts() -> None:
    from poop.types.int import Int

    result = _poop_str_from(Int(42))
    assert isinstance(result, Str)
    assert result._value == "42"


def test_str_from_float_converts() -> None:
    from poop.types.float import Float

    result = _poop_str_from(Float(3.14))
    assert isinstance(result, Str)
    assert result._value == "3.14"


def test_str_from_bool_converts() -> None:
    from poop.types.boolean import false, true

    assert _poop_str_from(true)._value == "True"
    assert _poop_str_from(false)._value == "False"
