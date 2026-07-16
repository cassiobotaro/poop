import ast

from poop.interpreter import Interpreter
from poop.transformers import DEFAULT_TRANSFORMERS
from poop.transformers.class_ import ClassTransformer
from poop.transformers.object import ObjectTransformer
from poop.types.object import Object


def _names(source: str) -> list[str]:
    tree = ObjectTransformer().transform(ast.parse(source))
    return [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]


def test_bare_object_is_rewritten() -> None:
    # It was the one lowercase builtin with no Name-position rewrite, so it
    # reached runtime as the raw CPython class.
    assert _names("object") == ["_poop_object"]


def test_object_is_rewritten_wherever_it_is_named() -> None:
    assert "_poop_object" in _names("x.is_instance(object)")
    assert "_poop_object" in _names("f = object")


def test_capital_object_is_a_real_name_now() -> None:
    # `Object` was accepted only as a class-base string and was a NameError
    # everywhere else; it now resolves like `object`, in every position.
    assert _names("Object") == ["_poop_object"]
    assert "_poop_object" in _names("Object.print()")
    assert "_poop_object" in _names("x.is_instance(Object)")


def test_other_names_are_untouched() -> None:
    assert _names("objects") == ["objects"]
    assert _names("my_object") == ["my_object"]
    assert _names("Objection") == ["Objection"]


def test_declares_no_bindings_because_class_transformer_owns_the_name() -> None:
    # The namespace build raises on a duplicate key rather than letting one
    # transformer silently overwrite another's binding.
    assert ObjectTransformer.BINDINGS == {}
    assert ClassTransformer.BINDINGS == {"_poop_object": Object}


def test_order_against_class_transformer_is_free() -> None:
    # Unlike ExceptionTransformer against RaiseTransformer, either order works:
    # whichever runs first leaves `_poop_object`, which the other no longer
    # matches. Asserted rather than assumed, since a silent dependency here is
    # exactly what bit proposal 12.
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
