import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_builtin_shadow import NoBuiltinShadowValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoBuiltinShadowValidator().validate(tree)


def test_assign_to_str_raises() -> None:
    tree = ast.parse("str = 'hello'")
    with pytest.raises(ValidationError, match="POOP builtin name"):
        NoBuiltinShadowValidator().validate(tree)


def test_assign_to_int_raises() -> None:
    tree = ast.parse("int = 5")
    with pytest.raises(ValidationError, match="'int'"):
        NoBuiltinShadowValidator().validate(tree)


def test_function_scope_assign_to_str_raises() -> None:
    tree = ast.parse(
        "class App:\n    def run(self):\n        str = 'x'\n        return str"
    )
    with pytest.raises(ValidationError, match="POOP builtin name"):
        NoBuiltinShadowValidator().validate(tree)


def test_parameter_named_dict_raises() -> None:
    tree = ast.parse("class Tag:\n    def __init__(self, dict):\n        return dict")
    with pytest.raises(ValidationError, match="POOP builtin name"):
        NoBuiltinShadowValidator().validate(tree)


def test_lambda_parameter_named_list_raises() -> None:
    tree = ast.parse("f = lambda list: list")
    with pytest.raises(ValidationError, match="POOP builtin name"):
        NoBuiltinShadowValidator().validate(tree)


def test_class_named_int_raises() -> None:
    tree = ast.parse("class int:\n    pass")
    with pytest.raises(ValidationError, match="POOP builtin name"):
        NoBuiltinShadowValidator().validate(tree)


def test_assign_to_slice_raises() -> None:
    # `slice` is rewritten to `_poop_slice` by SliceTransformer, so rebinding
    # it would silently clobber the runtime's Slice class.
    tree = ast.parse("slice = 3")
    with pytest.raises(ValidationError, match="'slice'"):
        NoBuiltinShadowValidator().validate(tree)


def test_constructor_call_passes() -> None:
    # Using the builtins as constructors is fine — only rebinding is blocked.
    tree = ast.parse("x = int('5')\ny = list((1, 2))")
    NoBuiltinShadowValidator().validate(tree)


def test_ordinary_name_passes() -> None:
    tree = ast.parse("integer = 5\nmy_list = (1, 2)")
    NoBuiltinShadowValidator().validate(tree)


def test_nested_def_named_dict_raises() -> None:
    # Nested defs bind a local name, so `def dict(): ...` inside a method
    # shadows the builtin the transformers rely on.
    source = (
        "class Demo:\n    def run(self):\n        def dict():\n            return 1"
    )
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="'dict'"):
        NoBuiltinShadowValidator().validate(tree)


def test_method_named_dict_is_fine() -> None:
    # Methods bind as class attributes, not in the enclosing scope.
    tree = ast.parse("class Demo:\n    def dict(self):\n        pass")
    NoBuiltinShadowValidator().validate(tree)


def test_assign_to_object_raises() -> None:
    # ObjectTransformer rewrites `object`/`Object` to `_poop_object` in every
    # position, Store included, so `object = 5` silently clobbers the root
    # class — the exact corruption this validator exists to stop.
    tree = ast.parse("object = 5")
    with pytest.raises(ValidationError, match="'object'"):
        NoBuiltinShadowValidator().validate(tree)


def test_assign_to_capital_object_raises() -> None:
    tree = ast.parse("Object = 5")
    with pytest.raises(ValidationError, match="'Object'"):
        NoBuiltinShadowValidator().validate(tree)


def test_parameter_named_object_raises() -> None:
    # Same hazard as a parameter named `dict`: body references rewrite to the
    # root class, not the argument.
    tree = ast.parse(
        "class Tag:\n    def __init__(self, object):\n        return object"
    )
    with pytest.raises(ValidationError, match="'object'"):
        NoBuiltinShadowValidator().validate(tree)


def test_object_as_base_class_is_fine() -> None:
    # Naming `Object`/`object` as a base is the sanctioned spelling; only
    # rebinding is blocked.
    tree = ast.parse("class Foo(Object):\n    pass\nclass Bar(object):\n    pass")
    NoBuiltinShadowValidator().validate(tree)
