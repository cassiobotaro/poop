import ast

from poop.errors import ValidationError


class NoAllValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAllVisitor().visit(tree)


class _NoAllVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "all":
            raise ValidationError(
                "all() is forbidden — use col.all(block) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
