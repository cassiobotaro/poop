import ast
from typing import ClassVar

from poop.types.boolean import false, true


class BooleanTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_true": true, "_poop_false": false}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _BooleanRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _BooleanRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is True:
            return ast.copy_location(ast.Name(id="_poop_true", ctx=ast.Load()), node)
        if node.value is False:
            return ast.copy_location(ast.Name(id="_poop_false", ctx=ast.Load()), node)
        return node
