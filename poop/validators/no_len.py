import ast

from poop.errors import ValidationError


class NoLenValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoLenVisitor().visit(tree)


class _NoLenVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "len":
            raise ValidationError(
                "len() is forbidden — use obj.len() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
