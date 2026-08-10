import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors


class NoSubscriptValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_NoSubscriptVisitor(), tree)


def _is_slice(node: ast.expr) -> bool:
    # A single-axis slice (`obj[a:b]`) is an `ast.Slice`; a multi-axis
    # slice (`obj[a:b, c:d]`) parses as an `ast.Tuple` whose elements
    # include `ast.Slice` nodes, so both must map to the slice guidance.
    if isinstance(node, ast.Slice):
        return True
    return isinstance(node, ast.Tuple) and any(
        isinstance(elt, ast.Slice) for elt in node.elts
    )


class _NoSubscriptVisitor(ErrorCollector):
    """Refuses `obj[key]`, naming the substitute for what the program *did*.

    Both messages named a reader, whatever the context. `xs[0] = 9` and
    `d["a"] = 1` were answered with "use obj.at(key) instead" — advice that
    reads where the program wrote, so a reader who follows it gets a value
    back, or a `KeyError`, for a program that was trying to store. The
    context is right there on the node: an `ast.Store` target is an
    assignment, and `at_put` is the message it wants.
    """

    def visit_Subscript(self, node: ast.Subscript) -> None:
        storing = isinstance(node.ctx, ast.Store)
        if _is_slice(node.slice):
            self.report(
                "slice assignment obj[start:stop] = value is forbidden — "
                "replace elements one at a time with obj.at_put(index, value)"
                if storing
                # A slice *write* has no whole-slice substitute, so this one
                # says what can be done rather than pointing at `slice`, which
                # only reads.
                else "slice obj[start:stop:step] is forbidden — use obj.slice(start, stop) or obj.slice(start, stop, step) instead",
                node,
            )
        else:
            self.report(
                "subscript obj[key] = value is forbidden — "
                "use obj.at_put(key, value) instead"
                if storing
                else "subscript obj[key] is forbidden — use obj.at(key) instead",
                node,
            )
        self.generic_visit(node)
