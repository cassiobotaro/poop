import ast

from poop.errors import ValidationError


class NoIssubclassValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoIssubclassVisitor().visit(tree)


class _NoIssubclassVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "issubclass":
            raise ValidationError(
                "issubclass() is forbidden — use Class.is_subclass(Other) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
