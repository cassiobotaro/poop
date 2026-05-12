import ast

from poop.transformers.slice import SliceTransformer
from poop.types.slice import Slice


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return SliceTransformer().transform(tree)


def test_slice_call_is_rewritten_to_mangled() -> None:
    tree = _transform("x = slice(1, 5)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_slice"


def test_slice_three_arg_is_rewritten() -> None:
    tree = _transform("x = slice(0, 10, 2)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_slice"
    assert len(call.args) == 3


def test_other_names_not_rewritten() -> None:
    tree = _transform("x = myslice(1, 5)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "myslice"


def test_bindings_contains_mangled_slice() -> None:
    assert "_poop_slice" in SliceTransformer.BINDINGS
    assert SliceTransformer.BINDINGS["_poop_slice"] is Slice
