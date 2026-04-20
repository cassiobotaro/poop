import ast

from poop.errors import ValidationError


class NoAbsValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAbsVisitor().visit(tree)


class _NoAbsVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "abs":
            raise ValidationError(
                "abs() is forbidden — use obj.abs() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
