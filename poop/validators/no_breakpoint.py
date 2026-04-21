import ast

from poop.errors import ValidationError


class NoBreakpointValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoBreakpointVisitor().visit(tree)


class _NoBreakpointVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "breakpoint":
            raise ValidationError(
                "breakpoint() is forbidden — no POOP equivalent",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
