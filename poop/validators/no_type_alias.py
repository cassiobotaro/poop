import ast

from poop.validators._node import NodeValidator


class NoTypeAliasValidator(NodeValidator):
    messages = {
        ast.TypeAlias: "type aliases are forbidden — POOP types differ from Python builtins"
    }
