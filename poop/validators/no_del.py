import ast

from poop.errors import ValidationError


class NoDelValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoDelVisitor().visit(tree)


class _NoDelVisitor(ast.NodeVisitor):
    def visit_Delete(self, node: ast.Delete) -> None:
        raise ValidationError(
            "del is forbidden — objects have no explicit destruction",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
