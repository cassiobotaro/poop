import ast

from poop.transformers.ellipsis import EllipsisTransformer
from poop.types.ellipsis import ellipsis


def _run(source: str) -> dict[str, object]:
    tree = EllipsisTransformer().transform(ast.parse(source))
    ns: dict[str, object] = dict(EllipsisTransformer.BINDINGS)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    return ns


def test_literal_becomes_poop_ellipsis() -> None:
    assert _run("x = ...")["x"] is ellipsis


def test_name_becomes_poop_ellipsis() -> None:
    # `Ellipsis` is the other spelling of the same value.
    assert _run("x = Ellipsis")["x"] is ellipsis


def test_ellipsis_in_a_collection_is_transformed() -> None:
    assert _run("x = [...]")["x"] == [ellipsis]


def test_bare_ellipsis_statement_is_transformed() -> None:
    # A stub body evaluates and discards, but must not evaluate a raw primitive.
    tree = EllipsisTransformer().transform(ast.parse("..."))
    stmt = tree.body[0]
    assert isinstance(stmt, ast.Expr)
    assert isinstance(stmt.value, ast.Name)
    assert stmt.value.id == "_poop_ellipsis"


def test_other_constants_are_left_alone() -> None:
    ns = _run("a = 1\nb = 'hi'\nc = None")
    assert ns["a"] == 1
    assert ns["b"] == "hi"
    assert ns["c"] is None


def test_unrelated_names_are_left_alone() -> None:
    assert _run("Ellipsisish = 1\nx = Ellipsisish")["x"] == 1


def test_location_is_preserved() -> None:
    tree = EllipsisTransformer().transform(ast.parse("x = ..."))
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    assert assign.value.lineno == 1
