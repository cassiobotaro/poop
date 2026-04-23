import ast

from poop.errors import ValidationError


class NoAssertValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAssertVisitor().visit(tree)


class _NoAssertVisitor(ast.NodeVisitor):
    def visit_Assert(self, node: ast.Assert) -> None:
        raise ValidationError(
            "assert is forbidden — use condition.assert_('message') instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
