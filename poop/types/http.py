from __future__ import annotations

import http as _http
import http.client as _http_client
import http.cookiejar as _http_cookiejar
import http.cookies as _http_cookies
import http.server as _http_server
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types._unwrap import _kwargs_from
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str


# CPython's HTTPStatus / HTTPMethod don't natively accept POOP `Int` /
# `Str` wrappers, because their IntEnum / StrEnum constructors call
# `int(value)` / `str(value)` and POOP wrappers don't match the
# inherited `_value_` comparison. Patch `_missing_` so they unwrap
# POOP types and recurse. This is additive — non-POOP Python code
# never passes POOP types, so the patch is a no-op for them.
def _http_status_missing(cls: Any, value: Any) -> Any:
    if isinstance(value, Int):
        return cls(value._value)
    return None


def _http_method_missing(cls: Any, value: Any) -> Any:
    if isinstance(value, Str):
        return cls(value._value)
    return None


_http.HTTPStatus._missing_ = classmethod(_http_status_missing)  # type: ignore[method-assign]  # ty: ignore[invalid-assignment]
_http.HTTPMethod._missing_ = classmethod(_http_method_missing)  # type: ignore[method-assign]  # ty: ignore[invalid-assignment]


class HTTPResponse(Object):
    """Wraps Python's `http.client.HTTPResponse` — the response object
    returned by `HTTPConnection.getresponse()`.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def status(self) -> Int:
        return Int(self._impl.status)

    @property
    def reason(self) -> Str:
        return Str(self._impl.reason)

    @property
    def version(self) -> Int:
        return Int(self._impl.version)

    @property
    def headers(self) -> Dict:
        result = Dict()
        for k, v in self._impl.getheaders():
            result.at_put(Str(k), Str(v))
        return result

    def read(self, amt: Int | None = None) -> Bytes:
        if amt is None:
            return Bytes(self._impl.read())
        return Bytes(self._impl.read(amt._value))

    def readline(self, limit: Int | None = None) -> Bytes:
        if limit is None:
            return Bytes(self._impl.readline())
        return Bytes(self._impl.readline(limit._value))

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def getheader(self, name: Str, default: Str | None = None) -> Str | NoneClass:
        result = self._impl.getheader(
            name._value, None if default is None else default._value
        )
        if result is None:
            return none
        return Str(result)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.close()


class HTTPConnection(Object):
    """Wraps Python's `http.client.HTTPConnection`."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        host: Str,
        port: Int | None = None,
        timeout: Int | None = None,
    ) -> None:
        kwargs = _kwargs_from(port=port, timeout=timeout)
        self._impl = _http_client.HTTPConnection(host._value, **kwargs)

    @classmethod
    def _from_impl(cls, impl: Any) -> HTTPConnection:
        obj = cls.__new__(cls)
        obj._impl = impl
        return obj

    def request(
        self,
        method: Str,
        url: Str,
        body: Bytes | Str | None = None,
        headers: Dict | None = None,
    ) -> NoneClass:
        kwargs = _kwargs_from(body=body)
        if headers is not None:
            h: dict[str, str] = {}
            for k, v in headers._data.items():
                if not (isinstance(k, Str) and isinstance(v, Str)):
                    raise TypeError("HTTP headers must map Str → Str")
                h[k._value] = v._value
            kwargs["headers"] = h
        self._impl.request(method._value, url._value, **kwargs)
        return none

    def getresponse(self) -> HTTPResponse:
        return HTTPResponse(self._impl.getresponse())

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def set_tunnel(
        self,
        host: Str,
        port: Int | None = None,
        headers: Dict | None = None,
    ) -> NoneClass:
        kwargs = _kwargs_from(port=port)
        if headers is not None:
            h: dict[str, str] = {}
            for k, v in headers._data.items():
                if not (isinstance(k, Str) and isinstance(v, Str)):
                    raise TypeError("set_tunnel headers must map Str → Str")
                h[k._value] = v._value
            kwargs["headers"] = h
        self._impl.set_tunnel(host._value, **kwargs)
        return none


class HTTPSConnection(HTTPConnection):
    """Wraps Python's `http.client.HTTPSConnection`."""

    def __init__(
        self,
        host: Str,
        port: Int | None = None,
        timeout: Int | None = None,
    ) -> None:
        kwargs = _kwargs_from(port=port, timeout=timeout)
        self._impl = _http_client.HTTPSConnection(host._value, **kwargs)


class HTTPClient:
    """Namespace mirroring Python's `http.client` module."""

    HTTPConnection: ClassVar[type[HTTPConnection]] = HTTPConnection
    HTTPSConnection: ClassVar[type[HTTPSConnection]] = HTTPSConnection
    HTTPResponse: ClassVar[type[HTTPResponse]] = HTTPResponse

    HTTPException: ClassVar[type[Exception]] = _http_client.HTTPException
    NotConnected: ClassVar[type[Exception]] = _http_client.NotConnected
    BadStatusLine: ClassVar[type[Exception]] = _http_client.BadStatusLine
    InvalidURL: ClassVar[type[Exception]] = _http_client.InvalidURL
    UnknownProtocol: ClassVar[type[Exception]] = _http_client.UnknownProtocol
    ResponseNotReady: ClassVar[type[Exception]] = _http_client.ResponseNotReady
    RemoteDisconnected: ClassVar[type[Exception]] = _http_client.RemoteDisconnected

    HTTP_PORT: ClassVar[Int] = Int(_http_client.HTTP_PORT)
    HTTPS_PORT: ClassVar[Int] = Int(_http_client.HTTPS_PORT)


class HTTPServerNamespace:
    """Namespace mirroring Python's `http.server` module.

    POOP exposes the handler / server classes as raw Python class
    refs — they're meant to be subclassed by hand, and writing a
    POOP-flavoured override of every dispatch slot in
    `BaseHTTPRequestHandler` would be churn for negligible gain.
    """

    BaseHTTPRequestHandler: ClassVar[type[Any]] = _http_server.BaseHTTPRequestHandler
    SimpleHTTPRequestHandler: ClassVar[type[Any]] = (
        _http_server.SimpleHTTPRequestHandler
    )
    CGIHTTPRequestHandler: ClassVar[type[Any]] = _http_server.CGIHTTPRequestHandler  # ty: ignore[deprecated]
    HTTPServer: ClassVar[type[Any]] = _http_server.HTTPServer
    ThreadingHTTPServer: ClassVar[type[Any]] = _http_server.ThreadingHTTPServer


class Morsel(Object):
    """Wraps Python's `http.cookies.Morsel` — one cookie value plus
    its attributes (Domain, Path, Secure, …).
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def key(self) -> Str:
        return Str(self._impl.key)

    @property
    def value(self) -> Str:
        return Str(self._impl.value)

    @property
    def coded_value(self) -> Str:
        return Str(self._impl.coded_value)

    def OutputString(self, attrs: List | None = None) -> Str:
        if attrs is None:
            return Str(self._impl.OutputString())
        names: list[str] = []
        for a in attrs:
            if not isinstance(a, Str):
                raise TypeError("Morsel.OutputString attrs must be Str")
            names.append(a._value)
        return Str(self._impl.OutputString(names))


class SimpleCookie(Object):
    """Wraps Python's `http.cookies.SimpleCookie` — a dict of `Morsel`s
    suitable for parsing `Cookie:` / `Set-Cookie:` headers.
    """

    __slots__ = ("_impl",)

    def __init__(self, source: Str | None = None) -> None:
        self._impl = _http_cookies.SimpleCookie(
            None if source is None else source._value
        )

    def load(self, rawdata: Str) -> NoneClass:
        self._impl.load(rawdata._value)
        return none

    def output(self, attrs: List | None = None, sep: Str | None = None) -> Str:
        kwargs: dict[str, Any] = {}
        if attrs is not None:
            kwargs["attrs"] = [a._value if isinstance(a, Str) else a for a in attrs]
        if sep is not None:
            kwargs["sep"] = sep._value
        return Str(self._impl.output(**kwargs))

    def at(self, key: Str) -> Morsel:
        return Morsel(self._impl[key._value])

    def at_put(self, key: Str, value: Str) -> NoneClass:
        self._impl[key._value] = value._value
        return none

    def keys(self) -> List:
        return List(*(Str(k) for k in self._impl.keys()))

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, Str):
            return False
        return key._value in self._impl

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class HTTPCookies:
    """Namespace mirroring Python's `http.cookies` module."""

    BaseCookie: ClassVar[type[Any]] = _http_cookies.BaseCookie
    SimpleCookie: ClassVar[type[SimpleCookie]] = SimpleCookie
    Morsel: ClassVar[type[Morsel]] = Morsel
    CookieError: ClassVar[type[Exception]] = _http_cookies.CookieError


class HTTPCookieJar:
    """Namespace mirroring Python's `http.cookiejar` module.

    Class refs only — `CookieJar` / `FileCookieJar` / `MozillaCookieJar`
    / `LWPCookieJar` / `Cookie` are passed by reference to other
    networking APIs (`urllib.request.HTTPCookieProcessor`, …) rather
    than constructed directly in user POOP code.
    """

    CookieJar: ClassVar[type[Any]] = _http_cookiejar.CookieJar
    FileCookieJar: ClassVar[type[Any]] = _http_cookiejar.FileCookieJar
    MozillaCookieJar: ClassVar[type[Any]] = _http_cookiejar.MozillaCookieJar
    LWPCookieJar: ClassVar[type[Any]] = _http_cookiejar.LWPCookieJar
    Cookie: ClassVar[type[Any]] = _http_cookiejar.Cookie
    DefaultCookiePolicy: ClassVar[type[Any]] = _http_cookiejar.DefaultCookiePolicy
    CookiePolicy: ClassVar[type[Any]] = _http_cookiejar.CookiePolicy


class Http:
    """Namespace mirroring Python's `http` package.

    `HTTPStatus` and `HTTPMethod` are re-exported directly from
    CPython (with a `_missing_` patch so POOP `Int` / `Str` wrappers
    resolve to members). Submodules `client` / `server` / `cookies` /
    `cookiejar` are exposed under attribute access.
    """

    HTTPStatus: ClassVar[type[Any]] = _http.HTTPStatus
    HTTPMethod: ClassVar[type[Any]] = _http.HTTPMethod

    client: ClassVar[type[HTTPClient]] = HTTPClient
    server: ClassVar[type[HTTPServerNamespace]] = HTTPServerNamespace
    cookies: ClassVar[type[HTTPCookies]] = HTTPCookies
    cookiejar: ClassVar[type[HTTPCookieJar]] = HTTPCookieJar
