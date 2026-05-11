import ast

from poop.validators._node import make_node_validator

NoGlobalValidator = make_node_validator(
    {
        ast.Global: "global is forbidden — state lives in instances, not in scope manipulation",
        ast.Nonlocal: "nonlocal is forbidden — state lives in instances, not in scope manipulation",
    }
)
