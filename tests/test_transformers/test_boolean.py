import ast

from poop.transformers.boolean import BooleanTransformer
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
