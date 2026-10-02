import ast

from poop.validators._node import NodeValidator


class NoRaiseValidator(NodeValidator):
    messages = {ast.Raise: "raise is forbidden — use ExcType.raise_('msg') instead"}
