import ast

from poop.errors import ValidationError


class _Visitor(ast.NodeVisitor):
    def __init__(self, protected: frozenset[str]) -> None:
        self._protected = protected

    def _check(self, name: str, node: ast.AST) -> None:
        if name in self._protected:
            raise ValidationError(
                f"{name!r} is a POOP namespace binding; reassigning it shadows the runtime entry point",
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )

    def _visit_target(self, target: ast.AST) -> None:
        # Handles `x = ...`, `x: T = ...`, `x += ...`, and unpacking
        # forms like `x, y = ...` / `[x, y] = ...` / `(*x,) = ...`.
        if isinstance(target, ast.Name):
            self._check(target.id, target)
        elif isinstance(target, ast.Tuple | ast.List):
            for elt in target.elts:
                self._visit_target(elt)
        elif isinstance(target, ast.Starred):
            self._visit_target(target.value)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._visit_target(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._visit_target(node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._visit_target(node.target)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node.name, node)
        self.generic_visit(node)


class NoNamespaceShadowValidator:
    def __init__(self) -> None:
        # Pull the set of user-facing entry points from
        # DEFAULT_NAMESPACE so the protected list stays in sync with
        # whatever the transformers register. Lazy import to avoid
        # validator → transformer eager-load at validators package
        # import time (the cycle would still close, but this keeps
        # the dependency clean).
        from poop.transformers import DEFAULT_NAMESPACE

        self._protected: frozenset[str] = frozenset(
            n for n in DEFAULT_NAMESPACE if not n.startswith("_poop_")
        )

    def validate(self, tree: ast.Module) -> None:
        _Visitor(self._protected).visit(tree)
