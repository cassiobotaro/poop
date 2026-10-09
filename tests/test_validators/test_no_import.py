import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_import import NoImportValidator


def test_import_raises_validation_error() -> None:
    tree = ast.parse("import os")
    with pytest.raises(ValidationError, match="import is forbidden"):
        NoImportValidator().validate(tree)


def test_import_from_raises_validation_error() -> None:
    tree = ast.parse("from os import getcwd")
    with pytest.raises(ValidationError, match="import is forbidden"):
        NoImportValidator().validate(tree)


def test_import_as_alias_raises() -> None:
    tree = ast.parse("import json as j")
    with pytest.raises(ValidationError, match="import is forbidden"):
        NoImportValidator().validate(tree)


def test_message_names_what_is_injected() -> None:
    tree = ast.parse("import math")
    with pytest.raises(ValidationError) as exc_info:
        NoImportValidator().validate(tree)
    assert "already in scope" in str(exc_info.value)
    assert "Try, With" in str(exc_info.value)


@pytest.mark.parametrize(
    "source",
    ["lazy import json", "lazy from os import getcwd"],
    ids=["lazy_import", "lazy_import_from"],
)
def test_lazy_import_is_the_same_ban(source: str) -> None:
    # Python 3.15's `lazy` (PEP 810) is a flag on the same two nodes, not a
    # node of its own, so the ban needs no new case — this pins that.
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="import is forbidden"):
        NoImportValidator().validate(tree)
