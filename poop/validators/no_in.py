import ast

from poop.validators._op import OpValidator


class NoInValidator(OpValidator):
    node_type = ast.Compare
    messages = {
        ast.In: "in operator is forbidden — use col.includes(x) instead",
        ast.NotIn: "not in operator is forbidden — use col.includes(x).not_() instead",
    }
