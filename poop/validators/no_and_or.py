import ast

from poop.errors import ValidationError


class NoAndOrValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAndOrVisitor().visit(tree)


class _NoAndOrVisitor(ast.NodeVisitor):
    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if isinstance(node.op, ast.And):
            raise ValidationError(
                "and operator is forbidden — use .and_(lambda: ...) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        if isinstance(node.op, ast.Or):
            raise ValidationError(
                "or operator is forbidden — use .or_(lambda: ...) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
