import ast

from poop import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.transformers.class_ import ClassTransformer
from poop.types.boolean import _FalseClass
from poop.types.object import Object


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return ClassTransformer().transform(tree)


def _first_class_bases(source: str) -> list[str]:
    tree = _transform(source)
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    return [b.id for b in cls.bases if isinstance(b, ast.Name)]


def test_class_without_base_gets_object() -> None:
    bases = _first_class_bases("class Foo: pass")
    assert bases == ["_poop_object"]


def test_class_with_object_base_gets_rewritten() -> None:
    bases = _first_class_bases("class Foo(object): pass")
    assert bases == ["_poop_object"]


def test_class_with_explicit_Object_base_gets_rewritten() -> None:
    bases = _first_class_bases("class Foo(Object): pass")
    assert bases == ["_poop_object"]


def test_class_with_custom_base_unchanged() -> None:
    bases = _first_class_bases("class Bar(Foo): pass")
    assert bases == ["Foo"]


def test_nested_class_also_transformed() -> None:
    source = "class Outer:\n    class Inner: pass"
    tree = _transform(source)
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    for cls in classes:
        assert any(
            isinstance(b, ast.Name) and b.id == "_poop_object" for b in cls.bases
        ), f"{cls.name} missing _poop_object base"


def test_class_transformer_bindings_contains_object() -> None:
    assert ClassTransformer.BINDINGS.get("_poop_object") is Object


def test_transformed_class_inherits_from_object_at_runtime() -> None:
    tree = _transform("class Dog: pass\nd = Dog()")
    ns = dict(DEFAULT_NAMESPACE)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["d"], Object)


def test_class_with_object_base_inherits_at_runtime() -> None:
    tree = _transform("class Cat(object): pass\nc = Cat()")
    ns = dict(DEFAULT_NAMESPACE)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["c"], Object)


def test_inherited_print_method_available() -> None:
    Interpreter().run_source("class Dog: pass\nDog().print()")


def test_inherited_is_none_returns_false() -> None:
    tree = _transform("class Dog: pass\nresult = Dog().is_none()")
    ns = dict(DEFAULT_NAMESPACE)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["result"], _FalseClass)
