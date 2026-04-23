import ast

from poop.transformers.boolean import BooleanTransformer, _poop_bool_from
from poop.types.boolean import false, true


def _first_value(source: str) -> ast.expr:
    tree = ast.parse(source)
    transformed = BooleanTransformer().transform(tree)
    assign = transformed.body[0]
    assert isinstance(assign, ast.Assign)
    return assign.value


def test_true_literal_replaced_by_poop_true_name() -> None:
    value = _first_value("x = True")
    assert isinstance(value, ast.Name)
    assert value.id == "_poop_true"


def test_false_literal_replaced_by_poop_false_name() -> None:
    value = _first_value("x = False")
    assert isinstance(value, ast.Name)
    assert value.id == "_poop_false"


def test_integer_constant_not_altered() -> None:
    value = _first_value("x = 1")
    assert isinstance(value, ast.Constant)
    assert value.value == 1


def test_string_constant_not_altered() -> None:
    value = _first_value("x = 'hello'")
    assert isinstance(value, ast.Constant)
    assert value.value == "hello"


def test_transformed_nodes_have_line_info() -> None:
    tree = ast.parse("x = True")
    transformed = BooleanTransformer().transform(tree)
    assign = transformed.body[0]
    assert isinstance(assign, ast.Assign)
    name_node = assign.value
    assert hasattr(name_node, "lineno")
    assert name_node.lineno == 1


def test_bindings_contain_true_and_false_singletons() -> None:
    bindings = BooleanTransformer.BINDINGS
    assert bindings["_poop_true"] is true
    assert bindings["_poop_false"] is false


def test_bindings_contain_bool_from_factory() -> None:
    assert BooleanTransformer.BINDINGS["_poop_bool_from"] is _poop_bool_from


def test_bool_call_is_rewritten() -> None:
    tree = ast.parse("bool(x)")
    transformed = BooleanTransformer().transform(tree)
    expr = transformed.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_bool_from"


def test_method_named_bool_is_not_rewritten() -> None:
    tree = ast.parse("x.bool()")
    transformed = BooleanTransformer().transform(tree)
    expr = transformed.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "bool"


# _poop_bool_from factory tests


def test_bool_from_no_arg_returns_false() -> None:
    assert _poop_bool_from() is false


def test_bool_from_true_singleton_returns_same() -> None:
    assert _poop_bool_from(true) is true


def test_bool_from_false_singleton_returns_same() -> None:
    assert _poop_bool_from(false) is false


def test_bool_from_truthy_value_returns_true() -> None:
    from poop.types.int import Int

    assert _poop_bool_from(Int(1)) is true


def test_bool_from_falsy_value_returns_false() -> None:
    from poop.types.int import Int

    assert _poop_bool_from(Int(0)) is false


def test_bool_from_nonempty_str_returns_true() -> None:
    from poop.types.string import Str

    assert _poop_bool_from(Str("hello")) is true


def test_bool_from_empty_str_returns_false() -> None:
    from poop.types.string import Str

    assert _poop_bool_from(Str("")) is false
