import http as _stdlib_http

import pytest

from poop.interpreter import Interpreter
from poop.types.dict import Dict
from poop.types.http import (
    Http,
    HTTPClient,
    HTTPConnection,
    HTTPCookieJar,
    HTTPCookies,
    HTTPResponse,
    HTTPSConnection,
    HTTPServerNamespace,
    Morsel,
    SimpleCookie,
)
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str

# --- HTTPStatus / HTTPMethod ---


def test_http_status_is_poop_intenum() -> None:
    # proposal 155: rebuilt over the POOP IntEnum base, not CPython's raw enum.
    from poop.types.enum import IntEnum

    assert Http.HTTPStatus is not _stdlib_http.HTTPStatus
    assert issubclass(Http.HTTPStatus, IntEnum)
    assert Http.HTTPStatus.OK.value == 200
    assert Http.HTTPStatus.OK.value_object() == Int(200)


def test_http_status_member_metadata() -> None:
    s = Http.HTTPStatus.NOT_FOUND
    assert s.value == 404
    assert s.phrase == Str("Not Found")
    assert isinstance(s.description, Str)


def test_http_status_predicates() -> None:
    from poop.types.boolean import true

    assert Http.HTTPStatus.OK.is_success is true
    assert Http.HTTPStatus.NOT_FOUND.is_client_error is true
    assert Http.HTTPStatus.INTERNAL_SERVER_ERROR.is_server_error is true
    assert Http.HTTPStatus.MOVED_PERMANENTLY.is_redirection is true
    assert Http.HTTPStatus.CONTINUE.is_informational is true


def test_http_status_lookup_by_poop_int() -> None:
    # The inherited _missing_ lets POOP Int round-trip to the right member.
    assert Http.HTTPStatus(Int(200)) is Http.HTTPStatus.OK
    assert Http.HTTPStatus(Int(404)) is Http.HTTPStatus.NOT_FOUND


def test_http_status_equality_returns_poop_boolean() -> None:
    # proposal 155 + 144: status dispatch via == answering a POOP Boolean.
    from poop.types.boolean import Boolean, false, true

    assert isinstance(Http.HTTPStatus.OK == Http.HTTPStatus.OK, Boolean)
    assert (Http.HTTPStatus.OK == Http.HTTPStatus.OK) is true
    assert (Http.HTTPStatus.OK == Http.HTTPStatus.NOT_FOUND) is false


def test_http_status_dispatch_via_interpreter() -> None:
    Interpreter().run_source(
        "(http.HTTPStatus(200) == http.HTTPStatus.OK).if_true(lambda: 'ok'.print())"
    )


def test_http_status_unknown_raises() -> None:
    with pytest.raises(ValueError):
        Http.HTTPStatus(Int(999))


def test_http_method_is_poop_strenum() -> None:
    from poop.types.enum import StrEnum

    assert Http.HTTPMethod is not _stdlib_http.HTTPMethod
    assert issubclass(Http.HTTPMethod, StrEnum)
    assert Http.HTTPMethod.GET.value == "GET"
    assert Http.HTTPMethod.GET.value_object() == Str("GET")


def test_http_method_lookup_by_poop_str() -> None:
    assert Http.HTTPMethod(Str("POST")) is Http.HTTPMethod.POST
    assert Http.HTTPMethod(Str("DELETE")) is Http.HTTPMethod.DELETE


# --- http.client constants / errors ---


def test_http_client_constants() -> None:
    assert HTTPClient.HTTP_PORT == Int(80)
    assert HTTPClient.HTTPS_PORT == Int(443)


def test_http_client_errors_exposed() -> None:
    assert issubclass(HTTPClient.HTTPException, Exception)
    assert issubclass(HTTPClient.BadStatusLine, HTTPClient.HTTPException)
    assert issubclass(HTTPClient.InvalidURL, HTTPClient.HTTPException)
    assert issubclass(HTTPClient.NotConnected, HTTPClient.HTTPException)
    assert issubclass(HTTPClient.ResponseNotReady, HTTPClient.HTTPException)


def test_http_client_class_refs() -> None:
    assert HTTPClient.HTTPConnection is HTTPConnection
    assert HTTPClient.HTTPSConnection is HTTPSConnection
    assert HTTPClient.HTTPResponse is HTTPResponse


# --- HTTPConnection / HTTPSConnection ---


def test_http_connection_construction_no_request() -> None:
    # We don't actually connect; just verify the wrapper accepts POOP
    # args and stores them.
    conn = HTTPConnection(Str("example.com"))
    assert isinstance(conn, HTTPConnection)
    conn.close()


def test_http_connection_with_port_and_timeout() -> None:
    conn = HTTPConnection(Str("example.com"), port=Int(8080), timeout=Int(5))
    assert isinstance(conn, HTTPConnection)
    conn.close()


def test_https_connection_construction() -> None:
    conn = HTTPSConnection(Str("example.com"), port=Int(443))
    assert isinstance(conn, HTTPSConnection)
    conn.close()


def test_http_connection_set_tunnel() -> None:
    conn = HTTPConnection(Str("proxy.example.com"))
    headers = Dict().at_put(Str("Proxy-Auth"), Str("token"))
    assert (
        conn.set_tunnel(Str("target.example.com"), port=Int(443), headers=headers)
        is none
    )
    conn.close()


def test_http_connection_request_rejects_non_str_headers() -> None:
    conn = HTTPConnection(Str("example.com"))
    bad_headers = Dict().at_put(Str("X"), Int(1))
    with pytest.raises(TypeError):
        conn.request(Str("GET"), Str("/"), headers=bad_headers)
    conn.close()


def test_http_connection_set_tunnel_rejects_non_str_headers() -> None:
    conn = HTTPConnection(Str("example.com"))
    bad_headers = Dict().at_put(Str("X"), Int(1))
    with pytest.raises(TypeError):
        conn.set_tunnel(Str("target.example.com"), headers=bad_headers)
    conn.close()


# --- http.server ---


def test_http_server_class_refs() -> None:
    assert HTTPServerNamespace.BaseHTTPRequestHandler is not None
    assert HTTPServerNamespace.SimpleHTTPRequestHandler is not None
    assert HTTPServerNamespace.CGIHTTPRequestHandler is not None
    assert HTTPServerNamespace.HTTPServer is not None
    assert HTTPServerNamespace.ThreadingHTTPServer is not None


# --- http.cookies ---


def test_simple_cookie_round_trip() -> None:
    c = SimpleCookie()
    c.at_put(Str("session"), Str("abc123"))
    output = c.output()
    assert isinstance(output, Str)
    assert "session=abc123" in output._value


def test_simple_cookie_load() -> None:
    c = SimpleCookie()
    c.load(Str("name=value; Path=/"))
    assert c.at(Str("name")).value == Str("value")


def test_simple_cookie_keys() -> None:
    c = SimpleCookie()
    c.at_put(Str("a"), Str("1"))
    c.at_put(Str("b"), Str("2"))
    keys = c.keys()
    assert isinstance(keys, List)
    assert keys == List(Str("a"), Str("b"))


def test_simple_cookie_contains() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    assert Str("k") in c
    assert Str("missing") not in c


def test_simple_cookie_output_with_attrs() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    morsel = c.at(Str("k"))
    morsel._impl["path"] = "/foo"
    out = c.output(attrs=List(Str("path")))
    assert "Path=/foo" in out._value


def test_morsel_properties() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    m = c.at(Str("k"))
    assert isinstance(m, Morsel)
    assert m.key == Str("k")
    assert m.value == Str("v")
    assert isinstance(m.coded_value, Str)


def test_morsel_output_string() -> None:
    c = SimpleCookie()
    c.at_put(Str("session"), Str("xyz"))
    m = c.at(Str("session"))
    out = m.OutputString()
    assert isinstance(out, Str)
    assert "session=xyz" in out._value


def test_http_cookies_class_refs() -> None:
    assert HTTPCookies.BaseCookie is not None
    assert HTTPCookies.SimpleCookie is SimpleCookie
    assert HTTPCookies.Morsel is Morsel
    assert issubclass(HTTPCookies.CookieError, Exception)


# --- http.cookiejar ---


def test_http_cookiejar_class_refs() -> None:
    assert HTTPCookieJar.CookieJar is not None
    assert HTTPCookieJar.FileCookieJar is not None
    assert HTTPCookieJar.MozillaCookieJar is not None
    assert HTTPCookieJar.LWPCookieJar is not None
    assert HTTPCookieJar.Cookie is not None
    assert HTTPCookieJar.DefaultCookiePolicy is not None
    assert HTTPCookieJar.CookiePolicy is not None


# --- Submodule attribute access ---


def test_http_submodules_accessible() -> None:
    assert Http.client is HTTPClient
    assert Http.server is HTTPServerNamespace
    assert Http.cookies is HTTPCookies
    assert Http.cookiejar is HTTPCookieJar


# --- Interpreter integration ---


def test_http_status_via_interpreter() -> None:
    # `.value` / `.name` are raw Python int/str on CPython's
    # HTTPStatus; the interpreter call just verifies the lookup runs
    # cleanly. Round-tripping into POOP types is the user's job
    # (`Int(x.value)` or similar) in idiomatic POOP code.
    Interpreter().run_source("http.HTTPStatus.OK")


def test_http_status_lookup_via_interpreter() -> None:
    Interpreter().run_source("http.HTTPStatus(200)")


def test_simple_cookie_via_interpreter() -> None:
    Interpreter().run_source(
        'c = SimpleCookie()\nc.at_put("k", "v")\nc.output().print()'
    )


# --- HTTPResponse via mock ---


class _MockHTTPResponseImpl:
    def __init__(self) -> None:
        self.status = 200
        self.reason = "OK"
        self.version = 11
        self._body = b"hello body"
        self._lines = [b"line1\n", b"line2\n", b""]
        self._line_idx = 0
        self.closed = False
        self.url = "http://example.com/"

    def read(self, amt: int | None = None) -> bytes:
        if amt is None:
            return self._body
        return self._body[:amt]

    def readline(self, limit: int = -1) -> bytes:
        if self._line_idx >= len(self._lines):
            return b""
        line = self._lines[self._line_idx]
        self._line_idx += 1
        return line if limit < 0 else line[:limit]

    def close(self) -> None:
        self.closed = True

    def getheaders(self) -> list[tuple[str, str]]:
        return [("Content-Type", "text/plain"), ("X-Foo", "bar")]

    def getheader(self, name: str, default: str | None = None) -> str | None:
        if name.lower() == "content-type":
            return "text/plain"
        return default


def _make_mock_response() -> HTTPResponse:
    return HTTPResponse(_MockHTTPResponseImpl())


def test_http_response_status_reason_version() -> None:
    r = _make_mock_response()
    assert r.status == Int(200)
    assert r.reason == Str("OK")
    assert r.version == Int(11)


def test_http_response_headers() -> None:
    r = _make_mock_response()
    h = r.headers
    assert isinstance(h, Dict)
    assert h.at(Str("Content-Type")) == Str("text/plain")


def test_http_response_read_full() -> None:
    from poop.types.bytes import Bytes

    r = _make_mock_response()
    assert r.read() == Bytes(b"hello body")


def test_http_response_read_size() -> None:
    from poop.types.bytes import Bytes

    r = _make_mock_response()
    assert r.read(Int(5)) == Bytes(b"hello")


def test_http_response_readline() -> None:
    from poop.types.bytes import Bytes

    r = _make_mock_response()
    assert r.readline() == Bytes(b"line1\n")


def test_http_response_readline_limit() -> None:
    from poop.types.bytes import Bytes

    r = _make_mock_response()
    line = r.readline(Int(3))
    assert isinstance(line, Bytes)


def test_http_response_close_returns_none() -> None:
    r = _make_mock_response()
    assert r.close() is none


def test_http_response_getheader_found() -> None:
    r = _make_mock_response()
    assert r.getheader(Str("Content-Type")) == Str("text/plain")


def test_http_response_getheader_default() -> None:
    r = _make_mock_response()
    result = r.getheader(Str("Missing"), default=Str("fallback"))
    assert result == Str("fallback")


def test_http_response_getheader_missing_returns_none() -> None:
    from poop.types.none import NoneClass

    r = _make_mock_response()
    assert isinstance(r.getheader(Str("Missing")), NoneClass)


def test_http_response_context_manager() -> None:
    r = _make_mock_response()
    with r as cm:
        assert cm is r


# --- SimpleCookie extras ---


def test_simple_cookie_with_source() -> None:
    c = SimpleCookie(Str("a=1; b=2"))
    assert c.at(Str("a")).value == Str("1")
    assert c.at(Str("b")).value == Str("2")


def test_simple_cookie_output_with_sep() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    out = c.output(sep=Str("; "))
    assert isinstance(out, Str)


def test_morsel_output_string_with_attrs() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    m = c.at(Str("k"))
    m._impl["path"] = "/foo"
    out = m.OutputString(List(Str("path")))
    assert "Path=/foo" in out._value


def test_morsel_output_string_rejects_non_str() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    m = c.at(Str("k"))
    with pytest.raises(TypeError):
        m.OutputString(List(Int(1)))


def test_simple_cookie_contains_non_str_returns_false() -> None:
    c = SimpleCookie()
    c.at_put(Str("k"), Str("v"))
    assert (Int(1) in c) is False


def test_http_status_lookup_by_poop_str_falls_through() -> None:
    # Str-valued lookup against HTTPStatus (which is an IntEnum) should
    # surface ValueError just like Python — our patched `_missing_`
    # only handles `Int`.
    with pytest.raises(ValueError):
        Http.HTTPStatus(Str("OK"))


def test_http_method_lookup_unknown_raises() -> None:
    with pytest.raises(ValueError):
        Http.HTTPMethod(Str("FROBNICATE"))


# --- HTTPConnection via mock ---


class _MockHTTPConnectionImpl:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def request(self, method: str, url: str, **kwargs) -> None:
        self.calls.append(("request", (method, url), kwargs))

    def getresponse(self) -> _MockHTTPResponseImpl:
        self.calls.append(("getresponse", (), {}))
        return _MockHTTPResponseImpl()

    def close(self) -> None:
        self.calls.append(("close", (), {}))

    def set_tunnel(self, host: str, **kwargs) -> None:
        self.calls.append(("set_tunnel", (host,), kwargs))


def _make_mock_connection() -> tuple[HTTPConnection, _MockHTTPConnectionImpl]:
    conn = HTTPConnection(Str("example.com"))
    conn.close()
    mock = _MockHTTPConnectionImpl()
    conn._impl = mock  # ty: ignore[invalid-assignment]
    return conn, mock


def test_http_connection_from_impl_classmethod() -> None:
    mock = _MockHTTPConnectionImpl()
    conn = HTTPConnection._from_impl(mock)
    assert conn._impl is mock


def test_http_connection_request_with_body_and_headers() -> None:
    from poop.types.bytes import Bytes

    conn, mock = _make_mock_connection()
    headers = Dict().at_put(Str("Content-Type"), Str("text/plain"))
    result = conn.request(
        Str("POST"), Str("/api"), body=Bytes(b"payload"), headers=headers
    )
    assert result is none
    assert mock.calls[0] == (
        "request",
        ("POST", "/api"),
        {"body": b"payload", "headers": {"Content-Type": "text/plain"}},
    )


def test_http_connection_request_str_body() -> None:
    conn, mock = _make_mock_connection()
    conn.request(Str("POST"), Str("/api"), body=Str("text-body"))
    assert mock.calls[0][2]["body"] == "text-body"


def test_http_connection_getresponse_via_mock() -> None:
    conn, _ = _make_mock_connection()
    response = conn.getresponse()
    assert isinstance(response, HTTPResponse)


def test_http_connection_set_tunnel_minimal() -> None:
    conn, mock = _make_mock_connection()
    assert conn.set_tunnel(Str("target.example.com")) is none
    assert mock.calls[0][1] == ("target.example.com",)
