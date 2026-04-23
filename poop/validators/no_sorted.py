import ast

from poop.errors import ValidationError


class NoSortedValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSortedVisitor().visit(tree)


class _NoSortedVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "sorted":
            raise ValidationError(
                "sorted() is forbidden — use col.sorted() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
