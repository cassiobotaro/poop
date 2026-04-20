import ast

from poop.errors import ValidationError


class NoMatchValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoMatchVisitor().visit(tree)


class _NoMatchVisitor(ast.NodeVisitor):
    def visit_Match(self, node: ast.Match) -> None:
        raise ValidationError(
            "match/case is forbidden — use polymorphism and if_true(block)/if_false(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
