import ast

from poop.errors import ValidationError


class NoUnaryPlusValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoUnaryPlusVisitor().visit(tree)


class _NoUnaryPlusVisitor(ast.NodeVisitor):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.UAdd):
            raise ValidationError(
                "unary plus is forbidden — write the value directly",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
