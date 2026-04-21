import ast

from poop.errors import ValidationError


class NoSubscriptValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSubscriptVisitor().visit(tree)


class _NoSubscriptVisitor(ast.NodeVisitor):
    def visit_Subscript(self, node: ast.Subscript) -> None:
        if not isinstance(node.slice, ast.Slice):
            raise ValidationError(
                "subscript obj[key] is forbidden — use obj.at(key) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
