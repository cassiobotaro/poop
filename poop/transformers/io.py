from poop.types.io import IO, BytesIO, StringIO

NAMESPACE: dict[str, object] = {
    "io": IO,
    "StringIO": StringIO,
    "BytesIO": BytesIO,
}
