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


def test_constructor_call_passes() -> None:
    # Using the builtins as constructors is fine — only rebinding is blocked.
    tree = ast.parse("x = int('5')\ny = list((1, 2))")
    NoBuiltinShadowValidator().validate(tree)


def test_ordinary_name_passes() -> None:
    tree = ast.parse("integer = 5\nmy_list = (1, 2)")
    NoBuiltinShadowValidator().validate(tree)
