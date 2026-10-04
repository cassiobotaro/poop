import ast

from poop.validators._node import NodeValidator


class NoGlobalValidator(NodeValidator):
    messages = {
        ast.Global: "global is forbidden — state lives in instances, not in scope manipulation",
        ast.Nonlocal: "nonlocal is forbidden — state lives in instances, not in scope manipulation",
    }
