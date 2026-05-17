from __future__ import annotations

import tempfile
from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.xml import ET, XML, Element, ElementTree


def _attrib() -> Dict:
    d = Dict()
    d.at_put(Str("k"), Str("v"))
    return d


def test_element_constructs_with_tag() -> None:
    e = Element(Str("a"))
    assert e.tag == Str("a")


def test_element_constructs_with_attrib() -> None:
    e = Element(Str("a"), _attrib())
    assert e.get(Str("k")) == Str("v")


def test_element_set_and_get() -> None:
    e = Element(Str("a"))
    e.set(Str("k"), Str("v"))
    assert e.get(Str("k")) == Str("v")


def test_element_get_default() -> None:
    e = Element(Str("a"))
    assert e.get(Str("missing"), Str("fallback")) == Str("fallback")


def test_element_get_missing_returns_none() -> None:
    e = Element(Str("a"))
    assert e.get(Str("missing")) is none


def test_element_text_and_tail() -> None:
    e = Element(Str("a"))
    e.set_text(Str("body"))
    e.set_tail(Str("trail"))
    assert e.text == Str("body")
    assert e.tail == Str("trail")


def test_element_text_unset_is_none() -> None:
    e = Element(Str("a"))
    assert e.text is none
    assert e.tail is none


def test_element_set_text_to_none() -> None:
    e = Element(Str("a"))
    e.set_text(Str("x"))
    e.set_text(none)
    assert e.text is none


def test_element_keys_items() -> None:
    e = Element(Str("a"), _attrib())
    assert e.keys() == List(Str("k"))
    items = e.items()
    assert items.len() == Int(1)


def test_element_append_and_iter() -> None:
    parent = Element(Str("parent"))
    child = Element(Str("child"))
    parent.append(child)
    children = list(parent)
    assert len(children) == 1
    assert children[0].tag == Str("child")


def test_element_extend() -> None:
    parent = Element(Str("parent"))
    parent.extend(List(Element(Str("a")), Element(Str("b"))))
    assert parent.len() == Int(2)


def test_element_extend_rejects_non_element() -> None:
    parent = Element(Str("p"))
    with pytest.raises(TypeError):
        parent.extend(List(Str("not-elem")))


def test_element_insert_and_remove() -> None:
    parent = Element(Str("p"))
    a = Element(Str("a"))
    b = Element(Str("b"))
    parent.append(a)
    parent.insert(Int(0), b)
    parent.remove(a)
    assert parent.len() == Int(1)


def test_element_clear() -> None:
    parent = Element(Str("p"))
    parent.set(Str("k"), Str("v"))
    parent.append(Element(Str("c")))
    parent.clear()
    assert parent.len() == Int(0)
    assert parent.get(Str("k")) is none


def test_element_find_and_findall() -> None:
    root = ET.fromstring(Str("<r><a/><b/><a/></r>"))
    a = root.find(Str("a"))
    assert isinstance(a, Element)
    assert a.tag == Str("a")
    all_a = root.findall(Str("a"))
    assert all_a.len() == Int(2)


def test_element_find_missing_returns_none() -> None:
    root = ET.fromstring(Str("<r/>"))
    assert root.find(Str("zzz")) is none


def test_element_findtext() -> None:
    root = ET.fromstring(Str("<r><a>hello</a></r>"))
    assert root.findtext(Str("a")) == Str("hello")


def test_element_findtext_default() -> None:
    root = ET.fromstring(Str("<r/>"))
    assert root.findtext(Str("a"), Str("fallback")) == Str("fallback")


def test_element_findtext_missing_returns_none() -> None:
    root = ET.fromstring(Str("<r/>"))
    assert root.findtext(Str("a")) is none


def test_element_iter() -> None:
    root = ET.fromstring(Str("<r><a/><b><c/></b></r>"))
    all_elements = root.iter()
    assert all_elements.len()._value >= 4


def test_element_iter_with_tag() -> None:
    root = ET.fromstring(Str("<r><a/><a/><b/></r>"))
    a_only = root.iter(Str("a"))
    assert a_only.len() == Int(2)


def test_element_iterfind() -> None:
    root = ET.fromstring(Str("<r><a/><b/><a/></r>"))
    assert root.iterfind(Str("a")).len() == Int(2)


def test_element_itertext() -> None:
    root = ET.fromstring(Str("<r>x<a>y</a>z</r>"))
    texts = root.itertext()
    assert texts.len()._value >= 1


def test_et_tostring_default_is_str() -> None:
    e = Element(Str("a"))
    result = ET.tostring(e)
    assert isinstance(result, Str)


def test_et_tostring_unicode_explicit() -> None:
    e = Element(Str("a"))
    assert isinstance(ET.tostring(e, Str("unicode")), Str)


def test_et_tostring_bytes() -> None:
    e = Element(Str("a"))
    result = ET.tostring(e, Str("utf-8"))
    assert isinstance(result, Bytes)


def test_et_xml_alias() -> None:
    e = ET.XML(Str("<r/>"))
    assert isinstance(e, Element)


def test_et_subelement() -> None:
    parent = Element(Str("parent"))
    child = ET.SubElement(parent, Str("child"), _attrib())
    assert child.tag == Str("child")
    assert parent.len() == Int(1)


def test_et_indent_does_not_raise() -> None:
    root = ET.fromstring(Str("<r><a/></r>"))
    assert ET.indent(root) is none


def test_et_indent_with_space_arg() -> None:
    root = ET.fromstring(Str("<r><a/></r>"))
    assert ET.indent(root, Str("    ")) is none


def test_elementtree_from_element() -> None:
    e = Element(Str("root"))
    tree = ElementTree(e)
    root = tree.getroot()
    assert isinstance(root, Element)
    assert root.tag == Str("root")


def test_elementtree_empty_getroot_is_none() -> None:
    tree = ElementTree()
    assert tree.getroot() is none


def test_elementtree_parse_and_write() -> None:
    with tempfile.TemporaryDirectory() as td:
        src = _PyPath(td) / "src.xml"
        src.write_text("<r><a>x</a></r>")
        tree = ET.parse(Str(str(src)))
        assert isinstance(tree, ElementTree)
        out = _PyPath(td) / "out.xml"
        assert tree.write(Str(str(out))) is none
        assert out.exists()


def test_elementtree_find_findall_findtext_iter() -> None:
    root = ET.fromstring(Str("<r><a>1</a><a>2</a></r>"))
    tree = ElementTree(root)
    found = tree.find(Str("a"))
    assert isinstance(found, Element)
    assert found.tag == Str("a")
    assert tree.findall(Str("a")).len() == Int(2)
    assert tree.findtext(Str("a")) == Str("1")
    assert tree.findtext(Str("zzz")) is none
    assert tree.findtext(Str("zzz"), Str("fb")) == Str("fb")
    all_iter = tree.iter()
    assert all_iter.len()._value >= 3
    only_a = tree.iter(Str("a"))
    assert only_a.len() == Int(2)


def test_et_class_refs() -> None:
    assert ET.Element is Element
    assert ET.ElementTree is ElementTree
    assert XML.ET is ET


def test_et_parse_error_class() -> None:
    with pytest.raises(ET.ParseError):
        ET.fromstring(Str("<not valid"))


# --- Interpreter integration ---


def test_xml_fromstring_via_interpreter() -> None:
    Interpreter().run_source('ET.fromstring("<r/>").tag.print()')


def test_xml_subelement_via_interpreter() -> None:
    Interpreter().run_source(
        'root = Element("r")\nET.SubElement(root, "a").tag.print()'
    )
