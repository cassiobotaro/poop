import ast

from poop.validators._node import make_node_validator

NoAssertValidator = make_node_validator(
    {ast.Assert: "assert is forbidden — use obj.assert_('message') instead"}
)
