import ast

from poop.errors import ValidationError


class NoInputValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoInputVisitor().visit(tree)


class _NoInputVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "input":
            raise ValidationError(
                "input() is forbidden — no POOP equivalent",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
