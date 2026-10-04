import ast

from poop.validators._node import NodeValidator


class NoAssertValidator(NodeValidator):
    messages = {ast.Assert: "assert is forbidden — use obj.assert_('message') instead"}
