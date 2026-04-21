import ast

from poop.errors import ValidationError


class NoHasattrValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoHasattrVisitor().visit(tree)


class _NoHasattrVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "hasattr":
            raise ValidationError(
                "hasattr() is forbidden — use obj.has_attr(name) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
