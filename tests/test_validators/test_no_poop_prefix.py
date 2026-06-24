import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_poop_prefix import NoPoopPrefixValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_name_raises() -> None:
    tree = ast.parse("x = _poop_int")
    with pytest.raises(ValidationError, match="_poop_int is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_call_raises() -> None:
    tree = ast.parse("_poop_list_from([1, 2])")
    with pytest.raises(ValidationError, match="_poop_list_from is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_attribute_raises() -> None:
    tree = ast.parse("obj._poop_inner")
    with pytest.raises(ValidationError, match="_poop_inner is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_class_name_raises() -> None:
    tree = ast.parse("class _poop_int:\n    pass")
    with pytest.raises(ValidationError, match="_poop_int is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_other_underscore_names_pass() -> None:
    tree = ast.parse("x = _private\ny = __dunder__")
    NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_carries_line_number() -> None:
    tree = ast.parse("x = 1\ny = _poop_anything")
    with pytest.raises(ValidationError) as exc_info:
        NoPoopPrefixValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_poop_prefixed_function_name_raises() -> None:
    tree = ast.parse("class C:\n    def _poop_foo(self):\n        return 1")
    with pytest.raises(ValidationError, match="_poop_foo is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_async_function_name_raises() -> None:
    tree = ast.parse("class C:\n    async def _poop_foo(self):\n        return 1")
    with pytest.raises(ValidationError, match="_poop_foo is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_def_parameter_raises() -> None:
    tree = ast.parse("class C:\n    def m(self, _poop_x):\n        return 1")
    with pytest.raises(ValidationError, match="_poop_x is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_lambda_parameter_raises() -> None:
    # The body never mentions the parameter, so visit_Name alone misses it.
    tree = ast.parse("f = lambda _poop_a: 1")
    with pytest.raises(ValidationError, match="_poop_a is forbidden"):
        NoPoopPrefixValidator().validate(tree)


def test_poop_prefixed_vararg_and_kwarg_raise() -> None:
    star = ast.parse("class C:\n    def m(self, *_poop_args):\n        return 1")
    with pytest.raises(ValidationError, match="_poop_args is forbidden"):
        NoPoopPrefixValidator().validate(star)
    dstar = ast.parse("class C:\n    def m(self, **_poop_kw):\n        return 1")
    with pytest.raises(ValidationError, match="_poop_kw is forbidden"):
        NoPoopPrefixValidator().validate(dstar)
