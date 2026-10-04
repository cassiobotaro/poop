import ast

from poop.validators._node import NodeValidator

_MESSAGE = (
    "import is forbidden — POOP is the language, not the library; "
    "the only names it injects (Try, With) are already in scope"
)


class NoImportValidator(NodeValidator):
    messages = {
        ast.Import: _MESSAGE,
        ast.ImportFrom: _MESSAGE,
    }
