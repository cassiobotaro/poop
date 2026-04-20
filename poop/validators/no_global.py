import ast

from poop.errors import ValidationError


class NoGlobalValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoGlobalVisitor().visit(tree)


class _NoGlobalVisitor(ast.NodeVisitor):
    def visit_Global(self, node: ast.Global) -> None:
        raise ValidationError(
            "global is forbidden — state lives in instances, not in scope manipulation",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        raise ValidationError(
            "nonlocal is forbidden — state lives in instances, not in scope manipulation",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
