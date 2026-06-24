import ast

import pytest

from poop.transformers.dict import (
    DictTransformer,
    _poop_dict_from,
    _poop_dict_from_pairs,
)
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return DictTransformer().transform(tree)


def test_dict_literal_is_rewritten() -> None:
    tree = _transform('x = {"a": 1}')
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_dict_from_pairs"
    assert len(call.args) == 2


def test_dict_call_is_rewritten() -> None:
    tree = _transform("dict(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_dict_from"


def test_dict_call_no_arg_is_rewritten() -> None:
    tree = _transform("dict()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_dict_from"
    assert len(expr.value.args) == 0


def test_method_named_dict_is_not_rewritten() -> None:
    tree = _transform("x.dict()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "dict"


def test_bindings_contains_poop_dict_from_pairs() -> None:
    assert "_poop_dict_from_pairs" in DictTransformer.BINDINGS


def test_bindings_contains_poop_dict_from() -> None:
    assert DictTransformer.BINDINGS["_poop_dict_from"] is _poop_dict_from


def test_poop_dict_from_pairs_factory() -> None:
    result = _poop_dict_from_pairs(Str("a"), Int(1), Str("b"), Int(2))
    assert isinstance(result, Dict)
    expected = Dict()
    expected._data[Str("a")] = Int(1)
    expected._data[Str("b")] = Int(2)
    assert result == expected


# _poop_dict_from factory tests


def test_dict_from_no_arg_returns_empty() -> None:
    result = _poop_dict_from()
    assert isinstance(result, Dict)
    assert result == Dict()


def test_dict_from_kwargs() -> None:
    # proposal 135: dict(a=1, b=2) keyword form.
    result = _poop_dict_from(a=Int(1), b=Int(2))
    expected = Dict()
    expected._data[Str("a")] = Int(1)
    expected._data[Str("b")] = Int(2)
    assert result == expected


def test_dict_from_mapping_and_kwargs() -> None:
    base = Dict()
    base._data[Str("p")] = Int(1)
    result = _poop_dict_from(base, q=Int(2))
    assert result.at(Str("p")) == Int(1)
    assert result.at(Str("q")) == Int(2)


def test_dict_kwargs_via_interpreter() -> None:
    from poop.interpreter import Interpreter

    Interpreter().run_source('dict(a=1, b=2).at("a").print()')


def test_dict_merge_helper() -> None:
    from poop.transformers.dict import _poop_dict_merge

    a = Dict()
    a._data[Str("x")] = Int(1)
    b = Dict()
    b._data[Str("y")] = Int(2)
    merged = _poop_dict_merge(a, b)
    assert merged.at(Str("x")) == Int(1)
    assert merged.at(Str("y")) == Int(2)


def test_dict_merge_later_overrides_earlier() -> None:
    from poop.transformers.dict import _poop_dict_merge

    a = Dict()
    a._data[Str("x")] = Int(1)
    b = Dict()
    b._data[Str("x")] = Int(99)
    assert _poop_dict_merge(a, b).at(Str("x")) == Int(99)


def test_dict_splat_via_interpreter() -> None:
    from poop.interpreter import Interpreter

    Interpreter().run_source('{**{"x": 1}, "y": 2}.at("y").print()')


def test_dict_call_double_splat_copies_mapping() -> None:
    # `dict(**other)` must not reach the bare `_poop_dict` class — Python's
    # `**` unpacking demands raw str keys but a POOP Dict carries Str keys,
    # so the splat is folded into a `_poop_dict_merge` instead.
    from poop.interpreter import Interpreter

    Interpreter().run_source(
        'other = {"a": 1, "b": 2}\n'
        "d = dict(**other)\n"
        "d.len().print()\n"  # 2
        'd.at("a").print()\n'  # 1
    )


def test_dict_call_named_and_double_splat_merge() -> None:
    from poop.interpreter import Interpreter

    Interpreter().run_source(
        'more = {"b": 9, "c": 3}\n'
        "d = dict(a=1, **more)\n"
        "d.len().print()\n"  # 3 (a, b, c)
        'd.at("b").print()\n'  # 9
    )


def test_dict_call_positional_and_double_splat_merge() -> None:
    from poop.interpreter import Interpreter

    Interpreter().run_source(
        'base = {"x": 0}\n'
        'more = {"b": 9, "c": 3}\n'
        "d = dict(base, y=5, **more)\n"
        "d.len().print()\n"  # 4 (x, y, b, c)
    )


def test_dict_from_dict_returns_shallow_copy() -> None:
    d = Dict()
    d._data[Str("x")] = Int(1)
    result = _poop_dict_from(d)
    assert result == d
    assert result is not d
    result._data[Str("y")] = Int(2)
    assert Str("y") not in d._data


def test_dict_from_list_of_tuples() -> None:
    pairs = List(Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2)))
    result = _poop_dict_from(pairs)
    assert isinstance(result, Dict)
    assert result.at(Str("a")) == Int(1)
    assert result.at(Str("b")) == Int(2)


def test_dict_from_tuple_of_tuples() -> None:
    pairs = Tuple(Tuple(Str("x"), Int(10)), Tuple(Str("y"), Int(20)))
    result = _poop_dict_from(pairs)
    assert isinstance(result, Dict)
    assert result.at(Str("x")) == Int(10)
    assert result.at(Str("y")) == Int(20)


def test_dict_from_entry_wrong_size_raises() -> None:
    with pytest.raises(TypeError):
        _poop_dict_from(List(Tuple(Str("a"), Int(1), Int(2))))


def test_dict_from_list_of_lists() -> None:
    pairs = List(List(Str("a"), Int(1)), List(Str("b"), Int(2)))
    result = _poop_dict_from(pairs)
    assert isinstance(result, Dict)
    assert result.at(Str("a")) == Int(1)
    assert result.at(Str("b")) == Int(2)


def test_dict_from_list_of_lists_wrong_size_raises() -> None:
    with pytest.raises(TypeError):
        _poop_dict_from(List(List(Str("a"), Int(1), Int(2))))


def test_dict_from_invalid_item_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot use"):
        _poop_dict_from(List(Int(1)))


def test_dict_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_dict_from(Int(42))


def test_dict_literal_with_unpacking_rewritten_to_merge() -> None:
    # proposal 142: a `**` display is now rewritten to _poop_dict_merge.
    tree = _transform("x = {**d, 'a': 1}")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Call)
    assert isinstance(assign.value.func, ast.Name)
    assert assign.value.func.id == "_poop_dict_merge"
