import ast

from poop.errors import ValidationError


class NoInvertValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoInvertVisitor().visit(tree)


class _NoInvertVisitor(ast.NodeVisitor):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.Invert):
            raise ValidationError(
                "bitwise invert operator is forbidden — use .bit_invert() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
