import ast

from poop.transformers.tuple import TupleTransformer, _poop_tuple
from poop.types.int import Int
from poop.types.tuple import Tuple


def test_tuple_literal_rewritten() -> None:
    tree = ast.parse("result = (1, 2, 3)")
    transformed = TupleTransformer().transform(tree)
    assign = transformed.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_tuple"


def test_tuple_literal_elements() -> None:
    tree = ast.parse("result = (1, 2)")
    transformed = TupleTransformer().transform(tree)
    assign = transformed.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_tuple"
    assert len(call.args) == 2


def test_store_context_preserved() -> None:
    tree = ast.parse("(a, b) = (1, 2)")
    transformed = TupleTransformer().transform(tree)
    src = ast.unparse(transformed)
    assert "_poop_tuple" not in src or src.count("_poop_tuple") == 1


def test_bindings_contain_factory() -> None:
    assert "_poop_tuple" in TupleTransformer.BINDINGS


def test_poop_tuple_factory() -> None:
    result = _poop_tuple(Int(1), Int(2))
    assert result == Tuple(Int(1), Int(2))
