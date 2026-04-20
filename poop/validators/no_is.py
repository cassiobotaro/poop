import ast

from poop.errors import ValidationError


class NoIsValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoIsVisitor().visit(tree)


class _NoIsVisitor(ast.NodeVisitor):
    def visit_Compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if isinstance(op, ast.Is):
                raise ValidationError(
                    "is operator is forbidden — use .is_none() for None checks or .is_identical(other) for identity",
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            if isinstance(op, ast.IsNot):
                raise ValidationError(
                    "is not operator is forbidden — use .not_none() for None checks or .not_identical(other) for identity",
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
        self.generic_visit(node)
