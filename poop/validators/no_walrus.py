import ast

from poop.validators._node import NodeValidator


class NoWalrusValidator(NodeValidator):
    messages = {
        ast.NamedExpr: ":= (walrus operator) is forbidden — use a separate assignment instead"
    }
