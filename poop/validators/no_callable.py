import ast

from poop.errors import ValidationError


class NoCallableValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoCallableVisitor().visit(tree)


class _NoCallableVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "callable":
            raise ValidationError(
                "callable() is forbidden — use obj.callable() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
