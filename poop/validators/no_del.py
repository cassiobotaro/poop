import ast

from poop.validators._node import NodeValidator


class NoDelValidator(NodeValidator):
    messages = {ast.Delete: "del is forbidden — objects have no explicit destruction"}
