import ast

from poop.validators._node import NodeValidator

# One tail for the four rows: they differ only in the first words, and a
# substitute reworded in one of them must not leave the other three behind.
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
