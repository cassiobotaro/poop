import ast

from poop.validators._node import make_node_validator

NoDelValidator = make_node_validator(
    {ast.Delete: "del is forbidden — objects have no explicit destruction"}
)
