import ast

from poop.transformers.float import FloatTransformer
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
