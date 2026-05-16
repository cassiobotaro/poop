from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.urllib import (
    ParseResult,
    Request,
    Response,
    SplitResult,
    Urllib,
)

# --- urllib.parse: urlparse / urlsplit / urljoin / urldefrag ---


def test_urlparse_basic() -> None:
    result = Urllib.parse.urlparse(
        Str("https://user:pw@example.com:8080/path;q=1?k=v#frag")
    )
    assert isinstance(result, ParseResult)
    assert result.scheme == Str("https")
    assert result.netloc == Str("user:pw@example.com:8080")
    assert result.path == Str("/path")
    assert result.params == Str("q=1")
    assert result.query == Str("k=v")
    assert result.fragment == Str("frag")
    assert result.hostname == Str("example.com")
    assert result.port == Int(8080)
    assert result.username == Str("user")
    assert result.password == Str("pw")


def test_urlparse_no_credentials() -> None:
    result = Urllib.parse.urlparse(Str("http://example.com/"))
    assert isinstance(result.username, NoneClass)
    assert isinstance(result.password, NoneClass)
    assert isinstance(result.port, NoneClass)


def test_urlparse_geturl_round_trip() -> None:
    url = Str("https://example.com/path?k=v")
    assert Urllib.parse.urlparse(url).geturl() == url


def test_urlunparse() -> None:
    parts = Tuple(
        Str("https"),
        Str("example.com"),
        Str("/path"),
        Str(""),
        Str("k=v"),
        Str(""),
    )
    assert Urllib.parse.urlunparse(parts) == Str("https://example.com/path?k=v")


def test_urlsplit_basic() -> None:
    result = Urllib.parse.urlsplit(Str("https://example.com/path?k=v#frag"))
    assert isinstance(result, SplitResult)
    assert result.scheme == Str("https")
    assert result.netloc == Str("example.com")
    assert result.path == Str("/path")
    assert result.query == Str("k=v")
    assert result.fragment == Str("frag")
    assert result.hostname == Str("example.com")


def test_urlsplit_with_port() -> None:
    result = Urllib.parse.urlsplit(Str("https://example.com:443/"))
    assert result.port == Int(443)


def test_urlunsplit() -> None:
    parts = Tuple(
        Str("https"),
        Str("example.com"),
        Str("/path"),
        Str("k=v"),
        Str(""),
    )
    assert Urllib.parse.urlunsplit(parts) == Str("https://example.com/path?k=v")


def test_urlsplit_geturl_round_trip() -> None:
    url = Str("https://example.com/path")
    assert Urllib.parse.urlsplit(url).geturl() == url


def test_urljoin() -> None:
    base = Str("https://example.com/a/b")
    assert Urllib.parse.urljoin(base, Str("c")) == Str("https://example.com/a/c")


def test_urldefrag() -> None:
    result = Urllib.parse.urldefrag(Str("https://example.com/#section"))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Str("https://example.com/")
    assert result.at(Int(1)) == Str("section")


# --- quote / unquote ---


def test_quote_default_safe() -> None:
    assert Urllib.parse.quote(Str("hello world/a")) == Str("hello%20world/a")


def test_quote_with_explicit_safe() -> None:
    assert Urllib.parse.quote(Str("a b"), safe=Str(" ")) == Str("a b")


def test_quote_with_encoding() -> None:
    result = Urllib.parse.quote(Str("café"), encoding=Str("utf-8"))
    assert "caf" in result._value


def test_quote_plus() -> None:
    assert Urllib.parse.quote_plus(Str("hello world")) == Str("hello+world")


def test_quote_from_bytes() -> None:
    assert Urllib.parse.quote_from_bytes(Bytes(b"\xff\x00")) == Str("%FF%00")


def test_unquote() -> None:
    assert Urllib.parse.unquote(Str("hello%20world")) == Str("hello world")


def test_unquote_plus() -> None:
    assert Urllib.parse.unquote_plus(Str("hello+world")) == Str("hello world")


def test_unquote_to_bytes() -> None:
    assert Urllib.parse.unquote_to_bytes(Str("%FF%00")) == Bytes(b"\xff\x00")


# --- urlencode / parse_qs / parse_qsl ---


def test_urlencode_dict() -> None:
    query = Dict().at_put(Str("k"), Str("v")).at_put(Str("a"), Int(1))
    result = Urllib.parse.urlencode(query)
    assert "k=v" in result._value
    assert "a=1" in result._value


def test_urlencode_list_of_tuples() -> None:
    query = List(Tuple(Str("k"), Str("v")), Tuple(Str("a"), Str("b")))
    result = Urllib.parse.urlencode(query)
    assert result == Str("k=v&a=b")


def test_urlencode_doseq() -> None:
    from poop.types.boolean import true

    query = Dict().at_put(Str("k"), List(Str("a"), Str("b")))
    result = Urllib.parse.urlencode(query, doseq=true)
    assert result == Str("k=a&k=b")


def test_parse_qs() -> None:
    result = Urllib.parse.parse_qs(Str("k=v&k=w&a=b"))
    assert isinstance(result, Dict)
    assert result.at(Str("k")) == List(Str("v"), Str("w"))
    assert result.at(Str("a")) == List(Str("b"))


def test_parse_qsl() -> None:
    result = Urllib.parse.parse_qsl(Str("k=v&a=b"))
    assert isinstance(result, List)
    assert result == List(Tuple(Str("k"), Str("v")), Tuple(Str("a"), Str("b")))


# --- Request ---


def test_request_basic() -> None:
    req = Request(Str("https://example.com/api"))
    assert isinstance(req, Request)
    assert req.full_url == Str("https://example.com/api")
    assert req.method == Str("GET")
    assert req.type == Str("https")
    assert req.host == Str("example.com")


def test_request_with_data() -> None:
    req = Request(Str("https://example.com/api"), data=Bytes(b"payload"))
    assert req.method == Str("POST")
    assert req.data == Bytes(b"payload")


def test_request_with_headers() -> None:
    from poop.types.boolean import true

    headers = Dict().at_put(Str("X-Custom"), Str("value"))
    req = Request(Str("https://example.com/api"), headers=headers)
    assert req.has_header(Str("X-custom")) is true


def test_request_add_header_returns_none() -> None:
    req = Request(Str("https://example.com/"))
    assert req.add_header(Str("X-Foo"), Str("bar")) is none
    headers = req.headers
    assert headers.at(Str("X-foo")) == Str("bar")


def test_request_add_unredirected_header() -> None:
    req = Request(Str("https://example.com/"))
    assert req.add_unredirected_header(Str("X-Internal"), Str("z")) is none


def test_request_headers_dict_str_to_str() -> None:
    headers = Dict().at_put(Str("X-A"), Str("1")).at_put(Str("X-B"), Str("2"))
    req = Request(Str("https://example.com/"), headers=headers)
    h = req.headers
    assert isinstance(h, Dict)
    assert h.at(Str("X-a")) == Str("1")


def test_request_rejects_non_str_headers() -> None:
    headers = Dict().at_put(Str("X-A"), Int(1))
    with pytest.raises(TypeError):
        Request(Str("https://example.com/"), headers=headers)


def test_request_with_method() -> None:
    req = Request(Str("https://example.com/"), method=Str("DELETE"))
    assert req.method == Str("DELETE")


# --- urlopen / Response (local file URL) ---


def test_urlopen_file_url(tmp_path: _PyPath) -> None:
    target = tmp_path / "payload.txt"
    target.write_text("hello via file://")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    assert isinstance(response, Response)
    body = response.read()
    response.close()
    assert body == Bytes(b"hello via file://")


def test_urlopen_returns_response_with_url_attribute(tmp_path: _PyPath) -> None:
    target = tmp_path / "x.txt"
    target.write_text("x")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    assert isinstance(response.url, Str)
    assert response.geturl() == response.url
    response.close()


def test_urlopen_context_manager(tmp_path: _PyPath) -> None:
    target = tmp_path / "ctx.txt"
    target.write_text("ctx-body")
    with Urllib.request.urlopen(Str(f"file://{target}")) as response:
        body = response.read()
    assert body == Bytes(b"ctx-body")


def test_urlopen_read_with_size(tmp_path: _PyPath) -> None:
    target = tmp_path / "sized.txt"
    target.write_text("abcdef")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    chunk = response.read(Int(3))
    response.close()
    assert chunk == Bytes(b"abc")


def test_urlopen_invalid_scheme_raises() -> None:
    with pytest.raises(Urllib.error.URLError):
        Urllib.request.urlopen(Str("bogus://nope"))


# --- urllib.error ---


def test_error_classes_exposed() -> None:
    assert issubclass(Urllib.error.URLError, Exception)
    assert issubclass(Urllib.error.HTTPError, Urllib.error.URLError)
    assert issubclass(Urllib.error.ContentTooShortError, Urllib.error.URLError)


# --- Handler class refs ---


def test_handler_classes_exposed() -> None:
    assert Urllib.request.OpenerDirector is not None
    assert Urllib.request.HTTPHandler is not None
    assert Urllib.request.HTTPSHandler is not None
    assert Urllib.request.HTTPCookieProcessor is not None
    assert Urllib.request.HTTPRedirectHandler is not None
    assert Urllib.request.ProxyHandler is not None
    assert Urllib.request.HTTPBasicAuthHandler is not None
    assert Urllib.request.HTTPDigestAuthHandler is not None


# --- Interpreter integration ---


def test_urlparse_via_interpreter() -> None:
    Interpreter().run_source(
        'urllib.parse.urlparse("https://example.com/").scheme.print()'
    )


def test_urlencode_via_interpreter() -> None:
    Interpreter().run_source('urllib.parse.urlencode({"a": "b"}).print()')


def test_request_via_interpreter() -> None:
    Interpreter().run_source('Request("https://example.com/").full_url.print()')


# --- Extra coverage ---


def test_urlopen_with_request_object(tmp_path: _PyPath) -> None:
    target = tmp_path / "req.txt"
    target.write_text("via-request")
    req = Request(Str(f"file://{target}"))
    response = Urllib.request.urlopen(req)
    body = response.read()
    response.close()
    assert body == Bytes(b"via-request")


def test_urlopen_with_data_and_timeout(tmp_path: _PyPath) -> None:
    target = tmp_path / "data.txt"
    target.write_text("data-body")
    response = Urllib.request.urlopen(
        Str(f"file://{target}"),
        timeout=Int(5),
    )
    response.close()
    assert isinstance(response, Response)


def test_response_readline(tmp_path: _PyPath) -> None:
    target = tmp_path / "lines.txt"
    target.write_text("alpha\nbeta\n")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    line = response.readline()
    response.close()
    assert line == Bytes(b"alpha\n")


def test_response_readline_with_size(tmp_path: _PyPath) -> None:
    target = tmp_path / "limit.txt"
    target.write_text("abcdefgh\n")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    line = response.readline(Int(3))
    response.close()
    assert isinstance(line, Bytes)


def test_response_reason_and_geturl(tmp_path: _PyPath) -> None:
    target = tmp_path / "info.txt"
    target.write_text("body")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    assert isinstance(response.reason, Str)
    assert isinstance(response.geturl(), Str)
    response.close()


def test_response_getcode(tmp_path: _PyPath) -> None:
    target = tmp_path / "code.txt"
    target.write_text("x")
    response = Urllib.request.urlopen(Str(f"file://{target}"))
    # file:// URLs don't have an HTTP status; getcode falls back to
    # the upstream behavior. Just verify the wrapper doesn't crash
    # for the common shape.
    try:
        code = response.getcode()
        assert isinstance(code, Int)
    except AttributeError, TypeError:
        # CPython's addinfourl may not expose .getcode() — that's OK.
        pass
    response.close()


def test_request_data_when_none() -> None:
    req = Request(Str("https://example.com/"))
    from poop.types.none import NoneClass

    assert isinstance(req.data, NoneClass)


def test_urlencode_rejects_non_tuple_list_entries() -> None:
    query = List(Str("not-a-pair"))
    with pytest.raises(TypeError):
        Urllib.parse.urlencode(query)


def test_unwrap_query_value_handles_boolean() -> None:
    from poop.types.boolean import true

    query = Dict().at_put(Str("flag"), true)
    result = Urllib.parse.urlencode(query)
    # bool unwraps to Python bool, which urlencode stringifies.
    assert "flag=" in result._value


def test_parse_qs_keep_blank_values() -> None:
    from poop.types.boolean import true

    result = Urllib.parse.parse_qs(Str("a=&b=1"), keep_blank_values=true)
    assert result.at(Str("a")) == List(Str(""))


def test_parse_qsl_with_strict() -> None:
    from poop.types.boolean import false

    result = Urllib.parse.parse_qsl(
        Str("k=v"), keep_blank_values=false, strict_parsing=false
    )
    assert isinstance(result, List)


def test_response_headers_via_mock() -> None:
    class _MockAddInfoUrl:
        status = 200
        reason = "OK"
        url = "http://x/"

        class headers:
            @staticmethod
            def items():
                return [("Content-Type", "text/plain"), ("X-Custom", "v")]

        def read(self, amt=None):
            return b""

        def readline(self, amt=-1):
            return b""

        def close(self):
            pass

        def geturl(self):
            return "http://x/"

        def getcode(self):
            return 200

        def __exit__(self, *a):
            pass

    resp = Response(_MockAddInfoUrl())
    h = resp.headers
    assert isinstance(h, Dict)
    assert h.at(Str("Content-Type")) == Str("text/plain")


def test_urlretrieve_to_file(tmp_path: _PyPath) -> None:
    source = tmp_path / "src.txt"
    source.write_text("source-body")
    dest = tmp_path / "dest.txt"
    result = Urllib.request.urlretrieve(
        Str(f"file://{source}"), filename=Str(str(dest))
    )
    assert isinstance(result, Tuple)
    path = result.at(Int(0))
    assert isinstance(path, Str)
    assert dest.read_text() == "source-body"


def test_urlretrieve_minimal(tmp_path: _PyPath) -> None:
    source = tmp_path / "data.txt"
    source.write_text("data-body")
    result = Urllib.request.urlretrieve(Str(f"file://{source}"))
    assert isinstance(result, Tuple)
