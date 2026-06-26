import ast

from poop.errors import ValidationError


class NoSubscriptValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSubscriptVisitor().visit(tree)


def _is_slice(node: ast.expr) -> bool:
    # A single-axis slice (`obj[a:b]`) is an `ast.Slice`; a multi-axis
    # slice (`obj[a:b, c:d]`) parses as an `ast.Tuple` whose elements
    # include `ast.Slice` nodes, so both must map to the slice guidance.
    if isinstance(node, ast.Slice):
        return True
    return isinstance(node, ast.Tuple) and any(
        isinstance(elt, ast.Slice) for elt in node.elts
    )


class _NoSubscriptVisitor(ast.NodeVisitor):
    def visit_Subscript(self, node: ast.Subscript) -> None:
        if _is_slice(node.slice):
            raise ValidationError(
                "slice obj[start:stop:step] is forbidden — use obj.slice(start, stop) or obj.slice(start, stop, step) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        raise ValidationError(
            "subscript obj[key] is forbidden — use obj.at(key) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
