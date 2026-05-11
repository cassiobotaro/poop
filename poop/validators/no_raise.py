import ast

from poop.validators._node import make_node_validator

NoRaiseValidator = make_node_validator(
    {ast.Raise: "raise is forbidden — use ExcType.raise_('msg') instead"}
)
