import ast

from poop.validators._node import NodeValidator

# One tail for the four rows: they differed only in the first words, and a
# substitute reworded in one of them would have left the other three behind.
_SUBSTITUTE = "use col.map(block) or col.filter(block) instead"


class NoComprehensionValidator(NodeValidator):
    messages = {
        node: f"{kind} is forbidden — {_SUBSTITUTE}"
        for node, kind in (
            (ast.ListComp, "list comprehension"),
            (ast.SetComp, "set comprehension"),
            (ast.DictComp, "dict comprehension"),
            (ast.GeneratorExp, "generator expression"),
        )
    }
