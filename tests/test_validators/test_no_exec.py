import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_exec import NoExecValidator


def test_dunder_import_raises_validation_error() -> None:
    # __import__('os') is the builtin form of `import` (banned by
    # NoImportValidator) and bypasses POOP's injected, infected stdlib
    # namespaces by returning the raw uninfected module, so it must be
    # rejected like the other dynamic-loading builtins.
    tree = ast.parse("__import__('os')")
    with pytest.raises(ValidationError, match="__import__()"):
        NoExecValidator().validate(tree)
