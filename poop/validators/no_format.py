import ast

from poop.errors import ValidationError


class NoFormatValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoFormatVisitor().visit(tree)


class _NoFormatVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "format":
            raise ValidationError(
                "format() is forbidden — use obj.format(spec) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
