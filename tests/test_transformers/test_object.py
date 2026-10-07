import ast

import pytest

from poop.interpreter import Interpreter
from poop.transformers import DEFAULT_TRANSFORMERS
from poop.transformers.class_ import ClassTransformer
from poop.transformers.object import ObjectTransformer
from poop.types.object import Object
from tests._support import rewritten


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        # It was the one lowercase builtin with no Name-position rewrite, so it
        # reached runtime as the raw CPython class.
        ("object", "_poop_object"),
        ("x.is_instance(object)", "x.is_instance(_poop_object)"),
        ("f = object", "f = _poop_object"),
        # `Object` was accepted only as a class-base string and was a NameError
        # everywhere else; it now resolves like `object`, in every position.
        ("Object", "_poop_object"),
        ("Object.print()", "_poop_object.print()"),
        ("x.is_instance(Object)", "x.is_instance(_poop_object)"),
        # Other names are untouched.
        ("objects", "objects"),
        ("my_object", "my_object"),
        ("Objection", "Objection"),
    ],
)
def test_object_is_rewritten_wherever_it_is_named(source: str, expected: str) -> None:
    assert rewritten(ObjectTransformer(), source) == expected


def test_declares_no_binding_for_the_name_class_transformer_owns() -> None:
    # The namespace build raises on a duplicate key rather than letting one
    # transformer silently overwrite another's binding. The *call*-position
    # factory added here which is a different key: the name position
    # still resolves to the class `ClassTransformer` binds.
    assert "_poop_object" not in ObjectTransformer.BINDINGS
    assert set(ObjectTransformer.BINDINGS) == {"_poop_object_from"}
    assert {"_poop_object": Object} == ClassTransformer.BINDINGS


def test_order_against_class_transformer_is_free() -> None:
    # Either order works: whichever runs first leaves `_poop_object`, which the
    # other no longer matches. Asserted rather than assumed, since a silent
    # ordering dependency between transformers has bitten before.
    source = "class Foo(object):\n    pass\n"
    after = ObjectTransformer().transform(
        ClassTransformer().transform(ast.parse(source))
    )
    before = ClassTransformer().transform(
        ObjectTransformer().transform(ast.parse(source))
    )
    assert ast.dump(after) == ast.dump(before)


def test_object_answers_the_class_side_through_the_interpreter() -> None:
    Interpreter().run_source("object.name()\nobject.superclass()\n")


def test_class_with_object_base_still_works() -> None:
    Interpreter().run_source("class Foo(object):\n    pass\nFoo()\n")


def test_object_transformer_is_wired_in() -> None:
    assert any(isinstance(t, ObjectTransformer) for t in DEFAULT_TRANSFORMERS)
