import ast

from poop.transformers.int import IntTransformer
from poop.types.int import Int


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


def test_bindings_contains_int_class() -> None:
    assert IntTransformer.BINDINGS["_poop_int"] is Int
