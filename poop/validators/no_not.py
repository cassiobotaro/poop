import ast

from poop.errors import ValidationError


class NoNotValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoNotVisitor().visit(tree)


class _NoNotVisitor(ast.NodeVisitor):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.Not):
            raise ValidationError(
                "not operator is forbidden — use .not_() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
