from poop.types.collections import (
    CollectionsNamespace,
    Counter,
    DefaultDict,
    Deque,
    OrderedDict,
    namedtuple,
)

NAMESPACE: dict[str, object] = {
    "collections": CollectionsNamespace,
    # Entry points keep Python's exact casing (deque/defaultdict/
    # namedtuple are lowercase in CPython) — same precedent as enum's
    # `auto`.
    "Counter": Counter,
    "deque": Deque,
    "defaultdict": DefaultDict,
    "OrderedDict": OrderedDict,
    "namedtuple": namedtuple,
}
