from __future__ import annotations

import urllib.error as _urllib_error
import urllib.parse as _urllib_parse
import urllib.request as _urllib_request
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types._unwrap import _b, _kwargs_from, _opt_str
from poop.types.boolean import Boolean, to_boolean
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


class ParseResult(Object):
    """Wraps Python's `urllib.parse.ParseResult` — the six-component
    breakdown of a URL.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def scheme(self) -> Str:
        return Str(self._impl.scheme)

    @property
    def netloc(self) -> Str:
        return Str(self._impl.netloc)

    @property
    def path(self) -> Str:
        return Str(self._impl.path)

    @property
    def params(self) -> Str:
        return Str(self._impl.params)

    @property
    def query(self) -> Str:
        return Str(self._impl.query)

    @property
    def fragment(self) -> Str:
        return Str(self._impl.fragment)

    @property
    def hostname(self) -> Str | NoneClass:
        return none if self._impl.hostname is None else Str(self._impl.hostname)

    @property
    def port(self) -> Int | NoneClass:
        return none if self._impl.port is None else Int(self._impl.port)

    @property
    def username(self) -> Str | NoneClass:
        return none if self._impl.username is None else Str(self._impl.username)

    @property
    def password(self) -> Str | NoneClass:
        return none if self._impl.password is None else Str(self._impl.password)

    def geturl(self) -> Str:
        return Str(self._impl.geturl())

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class SplitResult(Object):
    """Wraps Python's `urllib.parse.SplitResult` — five-component URL
    breakdown (no `params` slot).
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def scheme(self) -> Str:
        return Str(self._impl.scheme)

    @property
    def netloc(self) -> Str:
        return Str(self._impl.netloc)

    @property
    def path(self) -> Str:
        return Str(self._impl.path)

    @property
    def query(self) -> Str:
        return Str(self._impl.query)

    @property
    def fragment(self) -> Str:
        return Str(self._impl.fragment)

    @property
    def hostname(self) -> Str | NoneClass:
        return none if self._impl.hostname is None else Str(self._impl.hostname)

    @property
    def port(self) -> Int | NoneClass:
        return none if self._impl.port is None else Int(self._impl.port)

    def geturl(self) -> Str:
        return Str(self._impl.geturl())

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class UrllibParse:
    """Namespace mirroring Python's `urllib.parse` module.

    Pure-text URL transformations: parse / unparse / split / join,
    percent-encode (`quote*`), percent-decode (`unquote*`), and form
    encoding (`urlencode` / `parse_qs` / `parse_qsl`).
    """

    @staticmethod
    def urlparse(
        urlstring: Str,
        scheme: Str | None = None,
        allow_fragments: Boolean | None = None,
    ) -> ParseResult:
        return ParseResult(
            _urllib_parse.urlparse(
                urlstring._value,
                _opt_str(scheme, ""),
                _b(allow_fragments, True),
            )
        )

    @staticmethod
    def urlunparse(components: List | Tuple) -> Str:
        parts = [c._value if hasattr(c, "_value") else c for c in components]
        return Str(_urllib_parse.urlunparse(parts))

    @staticmethod
    def urlsplit(
        urlstring: Str,
        scheme: Str | None = None,
        allow_fragments: Boolean | None = None,
    ) -> SplitResult:
        return SplitResult(
            _urllib_parse.urlsplit(
                urlstring._value,
                _opt_str(scheme, ""),
                _b(allow_fragments, True),
            )
        )

    @staticmethod
    def urlunsplit(components: List | Tuple) -> Str:
        parts = [c._value if hasattr(c, "_value") else c for c in components]
        return Str(_urllib_parse.urlunsplit(parts))

    @staticmethod
    def urljoin(base: Str, url: Str, allow_fragments: Boolean | None = None) -> Str:
        return Str(
            _urllib_parse.urljoin(base._value, url._value, _b(allow_fragments, True))
        )

    @staticmethod
    def urldefrag(url: Str) -> Tuple:
        defrag, frag = _urllib_parse.urldefrag(url._value)
        return Tuple(Str(defrag), Str(frag))

    @staticmethod
    def quote(
        string: Str | Bytes,
        safe: Str | None = None,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Str:
        kwargs: dict[str, str] = {}
        kwargs.update(_kwargs_from(encoding=encoding, errors=errors))
        return Str(_urllib_parse.quote(string._value, _opt_str(safe, "/"), **kwargs))

    @staticmethod
    def quote_plus(
        string: Str | Bytes,
        safe: Str | None = None,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Str:
        kwargs: dict[str, str] = {}
        kwargs.update(_kwargs_from(encoding=encoding, errors=errors))
        return Str(
            _urllib_parse.quote_plus(string._value, _opt_str(safe, ""), **kwargs)
        )

    @staticmethod
    def quote_from_bytes(data: Bytes, safe: Str | None = None) -> Str:
        return Str(_urllib_parse.quote_from_bytes(data._value, _opt_str(safe, "/")))

    @staticmethod
    def unquote(
        string: Str,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Str:
        return Str(
            _urllib_parse.unquote(
                string._value,
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "replace"),
            )
        )

    @staticmethod
    def unquote_plus(
        string: Str,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Str:
        return Str(
            _urllib_parse.unquote_plus(
                string._value,
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "replace"),
            )
        )

    @staticmethod
    def unquote_to_bytes(string: Str | Bytes) -> Bytes:
        return Bytes(_urllib_parse.unquote_to_bytes(string._value))

    @staticmethod
    def urlencode(
        query: Dict | List | Tuple,
        doseq: Boolean | None = None,
        safe: Str | None = None,
        encoding: Str | None = None,
        errors: Str | None = None,
    ) -> Str:
        if isinstance(query, Dict):
            unwrapped: Any = {
                (k._value if hasattr(k, "_value") else k): _unwrap_query_value(v)
                for k, v in query._data.items()
            }
        else:
            unwrapped = []
            for pair in query:
                if not isinstance(pair, Tuple):
                    raise TypeError(
                        f"urlencode list entries must be Tuple, got {type(pair).__name__}"
                    )
                key: Any = pair.at(Int(0))
                value: Any = pair.at(Int(1))
                key_raw = key._value if hasattr(key, "_value") else key
                unwrapped.append((key_raw, _unwrap_query_value(value)))
        return Str(
            _urllib_parse.urlencode(
                unwrapped,
                doseq=_b(doseq, False),
                safe=_opt_str(safe, ""),
                encoding=_opt_str(encoding, "utf-8") if encoding else None,  # type: ignore[arg-type]
                errors=_opt_str(errors, "strict") if errors else None,  # type: ignore[arg-type]
            )
        )

    @staticmethod
    def parse_qs(
        qs: Str,
        keep_blank_values: Boolean | None = None,
        strict_parsing: Boolean | None = None,
    ) -> Dict:
        raw = _urllib_parse.parse_qs(
            qs._value,
            keep_blank_values=_b(keep_blank_values, False),
            strict_parsing=_b(strict_parsing, False),
        )
        result = Dict()
        for k, v in raw.items():
            result.at_put(Str(k), List(*(Str(item) for item in v)))
        return result

    @staticmethod
    def parse_qsl(
        qs: Str,
        keep_blank_values: Boolean | None = None,
        strict_parsing: Boolean | None = None,
    ) -> List:
        raw = _urllib_parse.parse_qsl(
            qs._value,
            keep_blank_values=_b(keep_blank_values, False),
            strict_parsing=_b(strict_parsing, False),
        )
        return List(*(Tuple(Str(k), Str(v)) for k, v in raw))


def _unwrap_query_value(value: Any) -> Any:
    if isinstance(value, Int | Float | Str | Bytes):
        return value._value
    if isinstance(value, Boolean):
        return bool(value)
    if isinstance(value, List | Tuple):
        items: list[Any] = []
        for item in value._items if isinstance(value, List | Tuple) else value:
            items.append(_unwrap_query_value(item))
        return items
    return value


class Request(Object):
    """Wraps Python's `urllib.request.Request` — an HTTP request object
    suitable for `urlopen`.

    Headers are read/written through `.add_header(key, value)` and
    `.headers` (a `Dict[Str, Str]`). The `data` slot accepts `Bytes`.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        url: Str,
        data: Bytes | None = None,
        headers: Dict | None = None,
        method: Str | None = None,
    ) -> None:
        header_dict: dict[str, str] = {}
        if headers is not None:
            for k, v in headers._data.items():
                if not (isinstance(k, Str) and isinstance(v, Str)):
                    raise TypeError("Request headers must map Str → Str")
                header_dict[k._value] = v._value
        # noqa: S310 — caller is responsible for URL scheme allowlisting.
        self._impl = _urllib_request.Request(  # noqa: S310
            url._value,
            data=None if data is None else data._value,
            headers=header_dict,
            method=None if method is None else method._value,
        )

    def add_header(self, key: Str, value: Str) -> NoneClass:
        self._impl.add_header(key._value, value._value)
        return none

    def add_unredirected_header(self, key: Str, value: Str) -> NoneClass:
        self._impl.add_unredirected_header(key._value, value._value)
        return none

    def has_header(self, key: Str) -> Boolean:

        return to_boolean(self._impl.has_header(key._value))

    @property
    def full_url(self) -> Str:
        return Str(self._impl.full_url)

    @property
    def method(self) -> Str:
        return Str(self._impl.get_method())

    @property
    def type(self) -> Str:
        return Str(self._impl.type)

    @property
    def host(self) -> Str:
        return Str(self._impl.host)

    @property
    def selector(self) -> Str:
        return Str(self._impl.selector)

    @property
    def data(self) -> Bytes | NoneClass:
        raw: Any = self._impl.data
        if raw is None:
            return none
        # `Request.data` can be a Buffer / SupportsRead / Iterable[bytes]
        # upstream; we only constructed with `Bytes` so it's safe to
        # coerce via `bytes(...)`.
        return Bytes(raw if isinstance(raw, bytes) else bytes(raw))

    @property
    def headers(self) -> Dict:
        result = Dict()
        for k, v in self._impl.headers.items():
            result.at_put(Str(k), Str(v))
        return result


class Response(Object):
    """Wraps an HTTP response from `urlopen` — the `http.client.HTTPResponse`
    or `urllib.response.addinfourl` returned by upstream `urlopen`.

    Exposes `.read()` (returns `Bytes`), `.status`, `.url`, `.headers`,
    `.close()`. `With`-friendly.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def read(self, size: Int | None = None) -> Bytes:
        if size is None:
            return Bytes(self._impl.read())
        return Bytes(self._impl.read(size._value))

    def readline(self, size: Int | None = None) -> Bytes:
        if size is None:
            return Bytes(self._impl.readline())
        return Bytes(self._impl.readline(size._value))

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    @property
    def status(self) -> Int:
        return Int(self._impl.status)

    @property
    def reason(self) -> Str:
        return Str(getattr(self._impl, "reason", ""))

    @property
    def url(self) -> Str:
        return Str(self._impl.url)

    @property
    def headers(self) -> Dict:
        result = Dict()
        for k, v in self._impl.headers.items():
            result.at_put(Str(k), Str(v))
        return result

    def geturl(self) -> Str:
        return Str(self._impl.geturl())

    def getcode(self) -> Int:
        return Int(self._impl.getcode())

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class UrllibRequest:
    """Namespace mirroring Python's `urllib.request` module.

    `urlopen(url, data=none, timeout=none)` returns a `Response`;
    `Request(url, data=none, headers=none, method=none)` is the
    request-builder class. The opener / handler hierarchy
    (`OpenerDirector`, `HTTPHandler`, `HTTPSHandler`, …) is exposed
    as raw Python class references for advanced callers.
    """

    Request: ClassVar[type[Request]] = Request
    Response: ClassVar[type[Response]] = Response

    OpenerDirector: ClassVar[type[Any]] = _urllib_request.OpenerDirector
    HTTPHandler: ClassVar[type[Any]] = _urllib_request.HTTPHandler
    HTTPSHandler: ClassVar[type[Any]] = _urllib_request.HTTPSHandler
    HTTPCookieProcessor: ClassVar[type[Any]] = _urllib_request.HTTPCookieProcessor
    HTTPRedirectHandler: ClassVar[type[Any]] = _urllib_request.HTTPRedirectHandler
    ProxyHandler: ClassVar[type[Any]] = _urllib_request.ProxyHandler
    HTTPBasicAuthHandler: ClassVar[type[Any]] = _urllib_request.HTTPBasicAuthHandler
    HTTPDigestAuthHandler: ClassVar[type[Any]] = _urllib_request.HTTPDigestAuthHandler
    ProxyBasicAuthHandler: ClassVar[type[Any]] = _urllib_request.ProxyBasicAuthHandler
    ProxyDigestAuthHandler: ClassVar[type[Any]] = _urllib_request.ProxyDigestAuthHandler
    HTTPDefaultErrorHandler: ClassVar[type[Any]] = (
        _urllib_request.HTTPDefaultErrorHandler
    )
    FileHandler: ClassVar[type[Any]] = _urllib_request.FileHandler
    DataHandler: ClassVar[type[Any]] = _urllib_request.DataHandler
    FTPHandler: ClassVar[type[Any]] = _urllib_request.FTPHandler
    CacheFTPHandler: ClassVar[type[Any]] = _urllib_request.CacheFTPHandler
    UnknownHandler: ClassVar[type[Any]] = _urllib_request.UnknownHandler

    @staticmethod
    def urlopen(
        url: Str | Request,
        data: Bytes | None = None,
        timeout: Float | Int | None = None,
    ) -> Response:
        target: Any = url._impl if isinstance(url, Request) else url._value
        kwargs = _kwargs_from(data=data, timeout=timeout)
        return Response(_urllib_request.urlopen(target, **kwargs))  # noqa: S310

    @staticmethod
    def urlretrieve(
        url: Str,
        filename: Str | None = None,
        data: Bytes | None = None,
    ) -> Tuple:
        kwargs = _kwargs_from(filename=filename, data=data)
        path, headers = _urllib_request.urlretrieve(  # noqa: S310 — caller responsibility
            url._value, **kwargs
        )
        return Tuple(Str(path), Str(str(headers)))


class UrllibError:
    """Namespace mirroring Python's `urllib.error` module."""

    URLError: ClassVar[type[Exception]] = _urllib_error.URLError
    HTTPError: ClassVar[type[Exception]] = _urllib_error.HTTPError
    ContentTooShortError: ClassVar[type[Exception]] = _urllib_error.ContentTooShortError


class Urllib:
    """Namespace mirroring Python's `urllib` package — `urllib.parse`,
    `urllib.request`, `urllib.error` exposed under their submodule
    names. `urllib.robotparser` is out of scope for v1.
    """

    parse: ClassVar[type[UrllibParse]] = UrllibParse
    request: ClassVar[type[UrllibRequest]] = UrllibRequest
    error: ClassVar[type[UrllibError]] = UrllibError
