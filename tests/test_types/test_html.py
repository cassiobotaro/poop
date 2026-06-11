from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.html import HTML, Entities, HTMLParser
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_escape_default_quotes() -> None:
    assert HTML.escape(Str('<a href="x">')) == Str("&lt;a href=&quot;x&quot;&gt;")


def test_escape_without_quotes() -> None:
    assert HTML.escape(Str('"<a>"'), false) == Str('"&lt;a&gt;"')


def test_escape_with_quote_true() -> None:
    assert HTML.escape(Str('"<a>"'), true) == Str("&quot;&lt;a&gt;&quot;")


def test_unescape() -> None:
    assert HTML.unescape(Str("&lt;a&gt;&amp;b")) == Str("<a>&b")


def test_has_entity_known_returns_true() -> None:
    assert HTML.has_entity(Str("amp")) is true


def test_has_entity_unknown_returns_false() -> None:
    assert HTML.has_entity(Str("not_a_real_entity_name")) is false


def test_entities_name2codepoint_is_dict_attr() -> None:
    d = Entities.name2codepoint
    assert isinstance(d, Dict)
    assert d.at(Str("amp")) == Int(38)


def test_entities_codepoint2name_is_dict_attr() -> None:
    d = Entities.codepoint2name
    assert isinstance(d, Dict)
    assert d.at(Int(38)) == Str("amp")


def test_entities_html5_is_dict_attr() -> None:
    d = Entities.html5
    assert isinstance(d, Dict)
    assert d.at(Str("amp;")) == Str("&")


def test_entities_entitydefs_is_dict_attr() -> None:
    d = Entities.entitydefs
    assert isinstance(d, Dict)


def test_parser_constructs() -> None:
    p = HTMLParser()
    assert isinstance(p, HTMLParser)


def test_parser_constructs_with_charrefs() -> None:
    p = HTMLParser(false)
    assert isinstance(p, HTMLParser)


def test_parser_feed_and_close() -> None:
    p = HTMLParser()
    assert p.feed(Str("<p>hi</p>")) is none
    assert p.close() is none


def test_parser_reset() -> None:
    p = HTMLParser()
    p.feed(Str("<p>hi"))
    assert p.reset() is none


def test_parser_getpos() -> None:
    p = HTMLParser()
    p.feed(Str("<p>hi"))
    pos = p.getpos()
    assert isinstance(pos, Tuple)
    assert pos.len() == Int(2)


def test_parser_get_starttag_text_after_feed() -> None:
    p = HTMLParser()
    p.feed(Str("<p>"))
    result = p.get_starttag_text()
    assert isinstance(result, Str)


def test_parser_get_starttag_text_initially_none() -> None:
    p = HTMLParser()
    assert p.get_starttag_text() is none


def test_parser_isinstance_of_html_parser_attr() -> None:
    p = HTML.parser()
    assert isinstance(p, HTMLParser)


def test_html_entities_class_attr() -> None:
    assert HTML.entities is Entities


# --- Interpreter integration ---


def test_html_escape_via_interpreter() -> None:
    Interpreter().run_source('html.escape("<a>").print()')


def test_html_unescape_via_interpreter() -> None:
    Interpreter().run_source('html.unescape("&lt;a&gt;").print()')


def test_html_parser_via_interpreter() -> None:
    Interpreter().run_source('HTMLParser().feed("<p>")')


# --- handler override bridging (proposal 161) ---


class _RecordingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[object, ...]] = []

    def handle_starttag(self, tag: Str, attrs: List) -> NoneClass:
        self.events.append(("start", tag, attrs))
        return none

    def handle_endtag(self, tag: Str) -> NoneClass:
        self.events.append(("end", tag))
        return none

    def handle_data(self, data: Str) -> NoneClass:
        self.events.append(("data", data))
        return none


def test_handle_data_override_fires_with_poop_str() -> None:
    p = _RecordingParser()
    p.feed(Str("<b>hi</b>"))
    data_events = [e for e in p.events if e[0] == "data"]
    assert len(data_events) == 1
    assert isinstance(data_events[0][1], Str)
    assert data_events[0][1] == Str("hi")


def test_handle_starttag_override_gets_poop_attrs() -> None:
    p = _RecordingParser()
    p.feed(Str('<a href="x">'))
    start = next(e for e in p.events if e[0] == "start")
    tag, attrs = start[1], start[2]
    assert isinstance(tag, Str)
    assert tag == Str("a")
    assert isinstance(attrs, List)
    assert attrs == List(Tuple(Str("href"), Str("x")))


def test_attr_without_value_is_none() -> None:
    p = _RecordingParser()
    p.feed(Str("<input disabled>"))
    start = next(e for e in p.events if e[0] == "start")
    assert start[2] == List(Tuple(Str("disabled"), none))


def test_startendtag_routes_through_starttag_default() -> None:
    # A subclass overriding only handle_starttag still sees self-closing tags,
    # because the default handle_startendtag delegates to it (CPython parity).
    p = _RecordingParser()
    p.feed(Str("<br/>"))
    assert any(e[0] == "start" and e[1] == Str("br") for e in p.events)


def test_non_overriding_subclass_does_not_crash() -> None:
    p = HTMLParser()
    assert p.feed(Str("<p>hi</p><br/>")) is none


def test_impl_ref_is_removed() -> None:
    # The raw-parser leak (_impl_ref) must no longer be reachable.
    assert not hasattr(HTMLParser(), "_impl_ref")
