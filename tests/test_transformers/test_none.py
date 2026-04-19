import ast

from poop.transformers.none import NoneTransformer
from poop.types.none import none


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return NoneTransformer().transform(tree)


def test_none_literal_is_rewritten() -> None:
    tree = _transform("x = None")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    name = assign.value
    assert isinstance(name, ast.Name)
    assert name.id == "_poop_none"


def test_other_constants_are_unchanged() -> None:
    tree = _transform("x = 42")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Constant)
    assert assign.value.value == 42


def test_bindings_contains_none() -> None:
    assert NoneTransformer.BINDINGS["_poop_none"] is none
