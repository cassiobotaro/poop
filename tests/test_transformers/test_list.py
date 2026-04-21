import ast

from poop.transformers.list import ListTransformer, _poop_list
from poop.types.int import Int
from poop.types.list import List


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return ListTransformer().transform(tree)


def test_list_literal_is_rewritten() -> None:
    tree = _transform("x = [1, 2, 3]")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_list"
    assert len(call.args) == 3


def test_empty_list_is_rewritten() -> None:
    tree = _transform("x = []")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_list"
    assert len(call.args) == 0


def test_store_context_not_rewritten() -> None:
    tree = _transform("[a, b] = (1, 2)")
    # Assignment target is a List node with Store context — must NOT be rewritten
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    target = assign.targets[0]
    assert isinstance(target, ast.List)


def test_bindings_contains_poop_list() -> None:
    assert "_poop_list" in ListTransformer.BINDINGS


def test_poop_list_factory() -> None:
    lst = _poop_list(Int(1), Int(2), Int(3))
    assert isinstance(lst, List)
    assert lst == List(Int(1), Int(2), Int(3))
