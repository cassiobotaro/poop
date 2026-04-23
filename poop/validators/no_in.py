import ast

from poop.errors import ValidationError


class NoInValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoInVisitor().visit(tree)


class _NoInVisitor(ast.NodeVisitor):
    def visit_Compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if isinstance(op, ast.In):
                raise ValidationError(
                    "in operator is forbidden — use col.includes(x) instead",
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            if isinstance(op, ast.NotIn):
                raise ValidationError(
                    "not in operator is forbidden — use col.includes(x).not_() instead",
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
        self.generic_visit(node)
