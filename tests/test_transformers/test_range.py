import ast

from poop.transformers.range import RangeTransformer, _poop_range
from poop.types.int import Int
from poop.types.range import Range


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return RangeTransformer().transform(tree)


def test_range_call_is_rewritten() -> None:
    tree = _transform("x = range(5)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_range"


def test_range_not_rewritten_for_other_names() -> None:
    tree = _transform("x = myrange(5)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "myrange"


def test_bindings_contains_poop_range() -> None:
    assert "_poop_range" in RangeTransformer.BINDINGS


# --- _poop_range helper ---


def test_poop_range_stop_only() -> None:
    iv = _poop_range(Int(5))
    assert isinstance(iv, Range)
    assert list(iv._iter()) == [Int(0), Int(1), Int(2), Int(3), Int(4)]


def test_poop_range_start_stop() -> None:
    iv = _poop_range(Int(2), Int(5))
    assert list(iv._iter()) == [Int(2), Int(3), Int(4)]


def test_poop_range_start_stop_step() -> None:
    iv = _poop_range(Int(1), Int(10), Int(2))
    assert list(iv._iter()) == [Int(1), Int(3), Int(5), Int(7), Int(9)]


def test_poop_range_empty() -> None:
    iv = _poop_range(Int(0))
    assert list(iv._iter()) == []
