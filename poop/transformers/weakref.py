from poop.types.weakref import (
    WeakKeyDictionary,
    WeakRef,
    Weakref,
    WeakSet,
    WeakValueDictionary,
)

NAMESPACE: dict[str, object] = {
    "weakref": Weakref,
    "WeakRef": WeakRef,
    "WeakSet": WeakSet,
    "WeakKeyDictionary": WeakKeyDictionary,
    "WeakValueDictionary": WeakValueDictionary,
}
