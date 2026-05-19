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
