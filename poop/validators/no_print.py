import ast

from poop.errors import ValidationError


class NoPrintValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoPrintVisitor().visit(tree)


class _NoPrintVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            raise ValidationError(
                "print is forbidden — use Transcript.show instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
