"""Shared machinery for the argument-forwarding builtin transformers.

``enumerate``/``zip``/``range`` repeat the same rewriting shape: a
``visit_Call`` routing ``<builtin>(...)`` through a converter binding
while forwarding *every* argument and keyword unchanged, and a
``visit_Name`` renaming the bare builtin to its mangled class binding.

This differs from ``_collection.py``'s ``CollectionRewriter``, which
guards on ``not node.keywords and len(node.args) <= 1`` and drops
keywords — so these three need their own factory rather than reusing it.
"""

import ast


def make_forwarding_rewriter(
    builtin: str, call_target: str, name_target: str
) -> type[ast.NodeTransformer]:
    """Build a rewriter routing ``builtin(...)`` calls and bare names.

    Args:
        builtin: The source name to intercept (e.g. ``"enumerate"``).
        call_target: Binding a ``builtin(...)`` call is rerouted to.
        name_target: Binding a bare ``builtin`` reference becomes.

    Returns:
        A ``NodeTransformer`` subclass forwarding all args and keywords.
    """

    class _ForwardingRewriter(ast.NodeTransformer):
        def visit_Call(self, node: ast.Call) -> ast.AST:
            if isinstance(node.func, ast.Name) and node.func.id == builtin:
                return ast.copy_location(
                    ast.Call(
                        func=ast.Name(id=call_target, ctx=ast.Load()),
                        args=[self.visit(arg) for arg in node.args],
                        keywords=[
                            ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                            for kw in node.keywords
                        ],
                    ),
                    node,
                )
            self.generic_visit(node)
            return node

        def visit_Name(self, node: ast.Name) -> ast.AST:
            if node.id == builtin:
                return ast.copy_location(ast.Name(id=name_target, ctx=node.ctx), node)
            return node

    return _ForwardingRewriter
