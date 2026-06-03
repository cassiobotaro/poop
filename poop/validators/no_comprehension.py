import ast

from poop.validators._node import make_node_validator

NoComprehensionValidator = make_node_validator(
    {
        ast.ListComp: "list comprehension is forbidden — use col.map(block) or col.filter(block) instead",
        ast.SetComp: "set comprehension is forbidden — use col.map(block) or col.filter(block) instead",
        ast.DictComp: "dict comprehension is forbidden — use col.map(block) or col.filter(block) instead",
        ast.GeneratorExp: "generator expression is forbidden — use col.map(block) or col.filter(block) instead",
    }
)
