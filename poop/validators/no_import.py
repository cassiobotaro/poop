import ast

from poop.validators._node import make_node_validator

_MESSAGE = (
    "import is forbidden — POOP injects its stdlib namespaces "
    "(math, os, json, …); the names are already in scope"
)

NoImportValidator = make_node_validator(
    {
        ast.Import: _MESSAGE,
        ast.ImportFrom: _MESSAGE,
    }
)
