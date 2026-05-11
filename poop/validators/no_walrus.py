import ast

from poop.validators._node import make_node_validator

NoWalrusValidator = make_node_validator(
    {
        ast.NamedExpr: ":= (walrus operator) is forbidden — use a separate assignment instead"
    }
)
