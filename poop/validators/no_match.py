import ast

from poop.validators._node import NodeValidator


class NoMatchValidator(NodeValidator):
    messages = {
        ast.Match: "match/case is forbidden — use polymorphism and if_true(block)/if_false(block) instead"
    }
