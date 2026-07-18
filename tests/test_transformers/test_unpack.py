import ast

from poop.interpreter import Interpreter
from poop.transformers.unpack import UnpackTransformer


def _transform(src: str) -> ast.Module:
    return UnpackTransformer().transform(ast.parse(src))


def test_starred_assign_appends_rebind() -> None:
    tree = _transform("c, *rest = xs")
    assert len(tree.body) == 2
    rebind = tree.body[1]
    assert isinstance(rebind, ast.Assign)
    assert isinstance(rebind.value, ast.Call)
    assert isinstance(rebind.value.func, ast.Name)
    assert rebind.value.func.id == "_poop_list_from"
    target = rebind.targets[0]
    assert isinstance(target, ast.Name)
    assert target.id == "rest"


def test_plain_assign_unchanged() -> None:
    tree = _transform("a, b = xs")
    assert len(tree.body) == 1


def test_nested_starred_rebinds_inner() -> None:
    tree = _transform("a, (b, *inner) = xs")
    assert len(tree.body) == 2
    rebind = tree.body[1]
    assert isinstance(rebind, ast.Assign)
    target = rebind.targets[0]
    assert isinstance(target, ast.Name)
    assert target.id == "inner"


def test_attribute_starred_target() -> None:
    tree = _transform("a, *self.rest = xs")
    assert len(tree.body) == 2
    rebind = tree.body[1]
    assert isinstance(rebind, ast.Assign)
    target = rebind.targets[0]
    assert isinstance(target, ast.Attribute)
    assert target.attr == "rest"


def test_rest_is_poop_list_via_interpreter() -> None:
    Interpreter().run_source("c, *rest = [1, 2, 3]\nrest.class_name().print()")


def test_rest_from_tuple_via_interpreter() -> None:
    Interpreter().run_source("a, *b = (1, 2, 3)\nb.len().print()")


def test_rest_from_str_via_interpreter() -> None:
    Interpreter().run_source("first, *others = 'xyz'\nothers.len().print()")


def test_rebind_tolerates_a_target_without_ctx() -> None:
    import ast

    from poop.transformers.unpack import _rebind

    # A rest-target is always a ctx-carrying assignable in practice; the guard
    # still degrades gracefully if handed a node type that carries no ctx.
    assign = _rebind(ast.Constant(value=1))
    assert isinstance(assign, ast.Assign)
    assert isinstance(assign.value, ast.Call)
