import pytest

from poop.interpreter import Interpreter
from poop.types.dict import Dict
from poop.types.string import Str, String, Template

# --- Module-level constants ---


def test_ascii_letters_constant() -> None:
    assert isinstance(String.ascii_letters, Str)
    assert (
        String.ascii_letters._value
        == "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )


def test_ascii_lowercase_constant() -> None:
    assert String.ascii_lowercase == Str("abcdefghijklmnopqrstuvwxyz")


def test_ascii_uppercase_constant() -> None:
    assert String.ascii_uppercase == Str("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_digits_constant() -> None:
    assert String.digits == Str("0123456789")


def test_hexdigits_constant() -> None:
    assert String.hexdigits == Str("0123456789abcdefABCDEF")


def test_octdigits_constant() -> None:
    assert String.octdigits == Str("01234567")


def test_punctuation_constant() -> None:
    assert isinstance(String.punctuation, Str)
    assert "!" in String.punctuation._value


def test_printable_includes_letters_and_digits() -> None:
    assert "a" in String.printable._value
    assert "0" in String.printable._value


def test_whitespace_constant() -> None:
    assert " " in String.whitespace._value
    assert "\t" in String.whitespace._value


# --- Template class ---


def test_template_substitute_replaces_variables() -> None:
    t = Template(Str("Hello, $name!"))
    mapping = Dict().at_put(Str("name"), Str("world"))
    assert t.substitute(mapping) == Str("Hello, world!")


def test_template_substitute_missing_raises() -> None:
    t = Template(Str("Hello, $name!"))
    with pytest.raises(KeyError):
        t.substitute(Dict())


def test_template_safe_substitute_leaves_missing() -> None:
    t = Template(Str("Hello, $name!"))
    assert t.safe_substitute(Dict()) == Str("Hello, $name!")


def test_template_template_property_returns_source() -> None:
    t = Template(Str("a/$b/c"))
    assert t.template == Str("a/$b/c")


def test_template_substitute_returns_str() -> None:
    t = Template(Str("$x"))
    mapping = Dict().at_put(Str("x"), Str("42"))
    result = t.substitute(mapping)
    assert isinstance(result, Str)


def test_template_substitute_braced_form() -> None:
    t = Template(Str("${greeting}, friend"))
    mapping = Dict().at_put(Str("greeting"), Str("hi"))
    assert t.substitute(mapping) == Str("hi, friend")


# --- Interpreter integration ---


def test_string_digits_reachable_via_interpreter() -> None:
    Interpreter().run_source("string.digits.print()")


def test_string_constant_count_reachable_via_interpreter() -> None:
    Interpreter().run_source('string.ascii_lowercase.count("a").print()')


def test_template_substitute_reachable_via_interpreter() -> None:
    Interpreter().run_source('Template("hi $who").substitute({"who": "POOP"}).print()')


def test_template_safe_substitute_reachable_via_interpreter() -> None:
    Interpreter().run_source('Template("$a/$b").safe_substitute({"a": "1"}).print()')
