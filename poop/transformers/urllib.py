from poop.types.urllib import (
    ParseResult,
    Request,
    Response,
    SplitResult,
    Urllib,
)

NAMESPACE: dict[str, object] = {
    "urllib": Urllib,
    "Request": Request,
    "Response": Response,
    "ParseResult": ParseResult,
    "SplitResult": SplitResult,
}
