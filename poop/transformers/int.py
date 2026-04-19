import ast

from poop.types.int import Int


class IntTransformer:
    BINDINGS: dict[str, object] = {"_poop_int": Int}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _IntRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _IntRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_int", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node
