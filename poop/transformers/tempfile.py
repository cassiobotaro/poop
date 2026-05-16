from poop.types.tempfile import (
    NamedTemporaryFile,
    SpooledTemporaryFile,
    TempfileNamespace,
    TemporaryDirectory,
    TemporaryFile,
)

NAMESPACE: dict[str, object] = {
    "tempfile": TempfileNamespace,
    "TemporaryFile": TemporaryFile,
    "NamedTemporaryFile": NamedTemporaryFile,
    "SpooledTemporaryFile": SpooledTemporaryFile,
    "TemporaryDirectory": TemporaryDirectory,
}
