from poop.types.collections import CollectionsNamespace, Counter, Deque

NAMESPACE: dict[str, object] = {
    "collections": CollectionsNamespace,
    "Counter": Counter,
    # Python exposes the class lowercase (collections.deque), so the
    # entry point mirrors that — same precedent as enum's `auto`.
    "deque": Deque,
}
