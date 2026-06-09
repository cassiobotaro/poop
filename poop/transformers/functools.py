from poop.types.functools import FunctoolsNamespace, Partial

NAMESPACE: dict[str, object] = {
    "functools": FunctoolsNamespace,
    # CPython exposes the class lowercase (functools.partial) — the
    # entry point mirrors that, like collections' deque.
    "partial": Partial,
}
