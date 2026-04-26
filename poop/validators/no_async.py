import ast

from poop.errors import ValidationError


class NoAsyncValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAsyncVisitor().visit(tree)


class _NoAsyncVisitor(ast.NodeVisitor):
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        raise ValidationError(
            "async functions are forbidden — POOP has no event loop",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_Await(self, node: ast.Await) -> None:
        raise ValidationError(
            "await is forbidden — POOP has no event loop",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
