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
    assert call.func.id == "_poop_slice_from"


def test_slice_three_arg_is_rewritten() -> None:
    tree = _transform("x = slice(0, 10, 2)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_slice_from"
    assert len(call.args) == 3


def test_slice_one_arg_injects_none_start() -> None:
    # CPython's slice(stop) means slice(None, stop): the lone argument is the
    # stop, so the rewrite must insert an implicit None start before it.
    tree = _transform("x = slice(5)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_slice_from"
    assert len(call.args) == 2
    start = call.args[0]
    assert isinstance(start, ast.Constant)
    assert start.value is None
    stop = call.args[1]
    assert isinstance(stop, ast.Constant)
    assert stop.value == 5


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
    # Proposal 44: a call goes through the factory, which guards the arity.
    # `Slice(...)` *is* the call — proposal 9 — so this was the one constructor
    # with no factory at all, and its refusal named `slice.__init__()`.
    assert "_poop_slice_from" in SliceTransformer.BINDINGS


def test_bare_slice_name_is_rewritten_to_the_mangled_binding() -> None:
    import ast

    from poop.transformers.slice import SliceTransformer

    tree = SliceTransformer().transform(ast.parse("f = slice"))
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Name)
    assert assign.value.id == "_poop_slice"
