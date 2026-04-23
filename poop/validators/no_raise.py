import ast

from poop.errors import ValidationError


class NoRaiseValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoRaiseVisitor().visit(tree)


class _NoRaiseVisitor(ast.NodeVisitor):
    def visit_Raise(self, node: ast.Raise) -> None:
        raise ValidationError(
            "raise is forbidden — use ExcType.raise_('msg') instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
