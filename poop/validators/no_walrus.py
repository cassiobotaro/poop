import ast

from poop.errors import ValidationError


class NoWalrusValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoWalrusVisitor().visit(tree)


class _NoWalrusVisitor(ast.NodeVisitor):
    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        raise ValidationError(
            ":= (walrus operator) is forbidden — use a separate assignment instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
