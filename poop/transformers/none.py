import ast

from poop.types.none import none


class NoneTransformer:
    BINDINGS: dict[str, object] = {"_poop_none": none}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _NoneRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _NoneRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is None:
            return ast.copy_location(ast.Name(id="_poop_none", ctx=ast.Load()), node)
        return node
