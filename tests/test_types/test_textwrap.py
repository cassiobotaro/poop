from poop.interpreter import Interpreter
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.textwrap import Textwrap, TextWrapper

# --- Module-level shortcuts ---


def test_wrap_splits_into_lines() -> None:
    text = Str("The quick brown fox jumps over the lazy dog")
    lines = Textwrap.wrap(text, width=Int(15))
    assert isinstance(lines, List)
    for line in lines:
        assert isinstance(line, Str)
        assert len(line._value) <= 15


def test_wrap_default_width() -> None:
    text = Str("hi")
    lines = Textwrap.wrap(text)
    assert lines == List(Str("hi"))


def test_fill_joins_with_newlines() -> None:
    text = Str("The quick brown fox jumps over the lazy dog")
    result = Textwrap.fill(text, width=Int(15))
    assert isinstance(result, Str)
    assert "\n" in result._value


def test_shorten_truncates_long_text() -> None:
    text = Str("Hello there friendly world")
    result = Textwrap.shorten(text, Int(12))
    assert isinstance(result, Str)
    assert len(result._value) <= 12


def test_shorten_keeps_short_text() -> None:
    text = Str("hello")
    result = Textwrap.shorten(text, Int(50))
    assert result == Str("hello")


def test_shorten_custom_placeholder() -> None:
    text = Str("one two three four five")
    result = Textwrap.shorten(text, Int(15), placeholder=Str("…"))
    assert "…" in result._value


def test_indent_prefixes_lines() -> None:
    text = Str("first\nsecond\n")
    result = Textwrap.indent(text, Str(">>> "))
    assert result == Str(">>> first\n>>> second\n")


def test_indent_with_predicate() -> None:
    text = Str("alpha\nbeta\ngamma\n")
    result = Textwrap.indent(
        text, Str("- "), predicate=lambda line: line._value.startswith("a")
    )
    assert result._value.count("- ") == 1
    assert "- alpha" in result._value


def test_dedent_strips_common_indent() -> None:
    text = Str("    line one\n    line two\n")
    result = Textwrap.dedent(text)
    assert result == Str("line one\nline two\n")


def test_dedent_handles_uneven_indents() -> None:
    text = Str("  one\n    two\n  three\n")
    result = Textwrap.dedent(text)
    assert result == Str("one\n  two\nthree\n")


# --- TextWrapper class ---


def test_text_wrapper_wrap_reuses_config() -> None:
    wrapper = TextWrapper(width=Int(20))
    lines = wrapper.wrap(Str("alpha beta gamma delta epsilon"))
    assert isinstance(lines, List)
    for line in lines:
        assert isinstance(line, Str)
        assert len(line._value) <= 20


def test_text_wrapper_fill_returns_str() -> None:
    wrapper = TextWrapper(width=Int(20))
    result = wrapper.fill(Str("alpha beta gamma delta epsilon"))
    assert isinstance(result, Str)


def test_text_wrapper_indents_first_line() -> None:
    wrapper = TextWrapper(width=Int(30), initial_indent=Str(">> "))
    result = wrapper.fill(Str("first second third"))
    assert result._value.startswith(">> ")


def test_text_wrapper_subsequent_indent() -> None:
    wrapper = TextWrapper(
        width=Int(20),
        initial_indent=Str(""),
        subsequent_indent=Str("    "),
    )
    result = wrapper.fill(Str("alpha beta gamma delta epsilon zeta"))
    lines = result._value.split("\n")
    if len(lines) > 1:
        assert lines[1].startswith("    ")


def test_text_wrapper_max_lines_with_placeholder() -> None:
    wrapper = TextWrapper(width=Int(10), max_lines=Int(1), placeholder=Str("..."))
    result = wrapper.fill(Str("one two three four five six"))
    assert result._value.endswith("...")


# --- Interpreter integration ---


def test_textwrap_wrap_reachable_via_interpreter() -> None:
    Interpreter().run_source('textwrap.wrap("abc def ghi", 5).len().print()')


def test_textwrap_dedent_reachable_via_interpreter() -> None:
    Interpreter().run_source('textwrap.dedent("  hi\\n  there\\n").print()')


def test_TextWrapper_reachable_via_interpreter() -> None:
    Interpreter().run_source('TextWrapper(15).fill("alpha beta gamma").print()')
