import ast

import pytest

from poop.transformers.bytes import BytesTransformer, _poop_bytes_from
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return BytesTransformer().transform(tree)


def test_bytes_literal_is_rewritten() -> None:
    tree = _transform("x = b'hello'")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_bytes"


def test_bytes_call_is_rewritten() -> None:
    tree = _transform("bytes(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_bytes_from"


def test_bytes_call_with_encoding_is_rewritten() -> None:
    tree = _transform('bytes(x, "utf-8")')
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_bytes_from"
    assert len(expr.value.args) == 2


def test_method_named_bytes_is_not_rewritten() -> None:
    tree = _transform("x.bytes()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "bytes"


def test_bindings_contains_bytes_class() -> None:
    assert BytesTransformer.BINDINGS["_poop_bytes"] is Bytes


def test_bindings_contains_bytes_from_factory() -> None:
    assert BytesTransformer.BINDINGS["_poop_bytes_from"] is _poop_bytes_from


# _poop_bytes_from factory tests


def test_bytes_from_no_arg_returns_empty() -> None:
    result = _poop_bytes_from()
    assert isinstance(result, Bytes)
    assert result._value == b""


def test_bytes_from_bytes_returns_same() -> None:
    x = Bytes(b"hello")
    assert _poop_bytes_from(x) is x


def test_bytes_from_int_returns_zero_filled() -> None:
    result = _poop_bytes_from(Int(3))
    assert isinstance(result, Bytes)
    assert result._value == b"\x00\x00\x00"


def test_bytes_from_str_uses_utf8_by_default() -> None:
    result = _poop_bytes_from(Str("hello"))
    assert isinstance(result, Bytes)
    assert result._value == b"hello"


def test_bytes_from_str_with_explicit_encoding() -> None:
    result = _poop_bytes_from(Str("hello"), Str("ascii"))
    assert isinstance(result, Bytes)
    assert result._value == b"hello"


def test_bytes_from_list_of_ints() -> None:
    result = _poop_bytes_from(List(Int(72), Int(101), Int(108)))
    assert isinstance(result, Bytes)
    assert result._value == b"Hel"


def test_bytes_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_bytes_from(Float(3.14))


def test_bare_bytes_name_is_rewritten_to_the_mangled_binding() -> None:
    import ast

    from poop.transformers.bytes import BytesTransformer

    tree = BytesTransformer().transform(ast.parse("f = bytes"))
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Name)
    assert assign.value.id == "_poop_bytes_cls"
