import ast

from poop.errors import ValidationError


class NoOpenValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoOpenVisitor().visit(tree)


class _NoOpenVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            raise ValidationError(
                "open() is forbidden — no POOP equivalent",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
