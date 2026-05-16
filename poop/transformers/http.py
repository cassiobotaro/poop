from poop.types.http import (
    Http,
    HTTPConnection,
    HTTPResponse,
    HTTPSConnection,
    Morsel,
    SimpleCookie,
)

NAMESPACE: dict[str, object] = {
    "http": Http,
    "HTTPConnection": HTTPConnection,
    "HTTPSConnection": HTTPSConnection,
    "HTTPResponse": HTTPResponse,
    "SimpleCookie": SimpleCookie,
    "Morsel": Morsel,
}
