import ast

from poop.errors import ValidationError


class NoTypeAliasValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoTypeAliasVisitor().visit(tree)


class _NoTypeAliasVisitor(ast.NodeVisitor):
    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        raise ValidationError(
            "type aliases are forbidden — POOP types differ from Python builtins",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
