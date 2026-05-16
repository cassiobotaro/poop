from poop.types.pickle import PickleNamespace, Pickler, Unpickler

NAMESPACE: dict[str, object] = {
    "pickle": PickleNamespace,
    "Pickler": Pickler,
    "Unpickler": Unpickler,
}
