import ast

from poop.errors import ValidationError


class NoSliceValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSliceVisitor().visit(tree)


class _NoSliceVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "slice":
            raise ValidationError(
                "slice() is forbidden — use obj.copy_from_to(start, stop) or obj.copy_from_to(start, stop, step) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
