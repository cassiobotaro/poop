import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_import import NoImportValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoImportValidator().validate(tree)


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


def test_message_names_substitute() -> None:
    tree = ast.parse("import math")
    with pytest.raises(ValidationError, match="already in scope"):
        NoImportValidator().validate(tree)
