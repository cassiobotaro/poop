from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.html import HTML, Entities, HTMLParser
from poop.types.int import Int
from poop.types.none import none
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


def test_entities_name2codepoint_returns_dict() -> None:
    d = Entities.name2codepoint()
    assert isinstance(d, Dict)
    assert d.at(Str("amp")) == Int(38)


def test_entities_codepoint2name_returns_dict() -> None:
    d = Entities.codepoint2name()
    assert isinstance(d, Dict)
    assert d.at(Int(38)) == Str("amp")


def test_entities_html5_returns_dict() -> None:
    d = Entities.html5()
    assert isinstance(d, Dict)
    assert d.at(Str("amp;")) == Str("&")


def test_entities_entitydefs_returns_dict() -> None:
    d = Entities.entitydefs()
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
