import ast

from poop.validators._node import make_node_validator

NoTypeAliasValidator = make_node_validator(
    {
        ast.TypeAlias: "type aliases are forbidden — POOP types differ from Python builtins"
    }
)
