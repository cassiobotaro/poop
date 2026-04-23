import ast

from poop.errors import ValidationError


class NoSubscriptValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSubscriptVisitor().visit(tree)


class _NoSubscriptVisitor(ast.NodeVisitor):
    def visit_Subscript(self, node: ast.Subscript) -> None:
        if isinstance(node.slice, ast.Slice):
            raise ValidationError(
                "slice obj[start:stop:step] is forbidden — use obj.copy_from_to(start, stop) or obj.copy_from_to(start, stop, step) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        raise ValidationError(
            "subscript obj[key] is forbidden — use obj.at(key) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
