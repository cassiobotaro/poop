import ast

from poop.validators._node import make_node_validator

NoMatchValidator = make_node_validator(
    {
        ast.Match: "match/case is forbidden — use polymorphism and if_true(block)/if_false(block) instead"
    }
)
