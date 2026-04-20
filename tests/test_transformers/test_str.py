import ast

from poop.transformers.string import StrTransformer
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
