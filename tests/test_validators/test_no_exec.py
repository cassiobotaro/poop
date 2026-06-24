import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_exec import NoExecValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoExecValidator().validate(tree)


def test_exec_raises_validation_error() -> None:
    tree = ast.parse("exec('x = 1')")
    with pytest.raises(ValidationError, match="exec()"):
        NoExecValidator().validate(tree)


def test_eval_raises_validation_error() -> None:
    tree = ast.parse("eval('1 + 1')")
    with pytest.raises(ValidationError, match="eval()"):
        NoExecValidator().validate(tree)


def test_compile_raises_validation_error() -> None:
    tree = ast.parse("compile('x = 1', '<str>', 'exec')")
    with pytest.raises(ValidationError, match="compile()"):
        NoExecValidator().validate(tree)


def test_dunder_import_raises_validation_error() -> None:
    # __import__('os') is the builtin form of `import` (banned by
    # NoImportValidator) and bypasses POOP's injected, infected stdlib
    # namespaces by returning the raw uninfected module, so it must be
    # rejected like the other dynamic-loading builtins.
    tree = ast.parse("__import__('os')")
    with pytest.raises(ValidationError, match="__import__()"):
        NoExecValidator().validate(tree)


def test_dunder_import_as_argument_raises_validation_error() -> None:
    tree = ast.parse("xs.map(__import__)")
    with pytest.raises(ValidationError, match="__import__"):
        NoExecValidator().validate(tree)


def test_exec_carries_line_number() -> None:
    tree = ast.parse("x = 1\nexec('x = 2')")
    with pytest.raises(ValidationError) as exc_info:
        NoExecValidator().validate(tree)
    assert exc_info.value.lineno == 2
