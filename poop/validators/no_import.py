import ast

from poop.validators._node import make_node_validator

_MESSAGE = (
    "import is forbidden — POOP is the language, not the library; "
    "the only names it injects (Try, With) are already in scope"
)

NoImportValidator = make_node_validator(
    {
        ast.Import: _MESSAGE,
        ast.ImportFrom: _MESSAGE,
    }
)
