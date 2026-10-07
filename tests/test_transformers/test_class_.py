import ast
from functools import partial

import pytest

from poop import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.transformers.class_ import ClassTransformer
from poop.types.boolean import _FalseClass
from poop.types.object import Object
from tests._support import rewritten, transform

_transform = partial(transform, ClassTransformer())


def _pipeline(source: str) -> ast.Module:
    # An explicit `object` / `Object` base is `ObjectTransformer`'s, which
    # rewrites both spellings in every position — so the base-list cases are
    # asserted on the whole pipeline rather than on `ClassTransformer` alone.
    return Interpreter().transform_source(source)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("class Foo: pass", "class Foo(_poop_object):\n    pass"),
        ("class Bar(Foo): pass", "class Bar(Foo):\n    pass"),
        (
            "class Outer:\n    class Inner: pass",
            "class Outer(_poop_object):\n\n    class Inner(_poop_object):\n        pass",
        ),
    ],
    ids=["without_base_gets_object", "custom_base_unchanged", "nested_class"],
)
def test_class_bases(source: str, expected: str) -> None:
    assert rewritten(ClassTransformer(), source) == expected


@pytest.mark.parametrize(
    "source", ["class Foo(object): pass", "class Foo(Object): pass"]
)
def test_class_with_an_explicit_object_base_gets_rewritten(source: str) -> None:
    assert ast.unparse(_pipeline(source)) == "class Foo(_poop_object):\n    pass"


def test_class_transformer_bindings_contains_object() -> None:
    assert ClassTransformer.BINDINGS.get("_poop_object") is Object


def test_transformed_class_inherits_from_object_at_runtime() -> None:
    tree = _transform("class Dog: pass\nd = Dog()")
    ns = dict(DEFAULT_NAMESPACE)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["d"], Object)


def test_class_with_object_base_inherits_at_runtime() -> None:
    tree = _pipeline("class Cat(object): pass\nc = Cat()")
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
