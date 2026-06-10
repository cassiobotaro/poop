from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.shlex import Shlex, Shlex_
from poop.types.string import Str

# --- Module-level functions ---


def test_split_simple_command() -> None:
    result = Shlex_.split(Str("echo hello world"))
    assert isinstance(result, List)
    assert result == List(Str("echo"), Str("hello"), Str("world"))


def test_split_quoted_args() -> None:
    result = Shlex_.split(Str('echo "hello world" foo'))
    assert result == List(Str("echo"), Str("hello world"), Str("foo"))


def test_shlex_do_iterates_tokens() -> None:
    # proposal 121: Shlex mixes in _IterableMixin, so .do works.
    collected: list[object] = []
    Shlex(Str("a b c")).do(lambda tok: collected.append(tok))
    assert collected == [Str("a"), Str("b"), Str("c")]


def test_split_with_comments() -> None:
    result = Shlex_.split(Str("echo foo # comment"), comments=true)
    assert result == List(Str("echo"), Str("foo"))


def test_join_round_trips() -> None:
    parts = List(Str("echo"), Str("hello"), Str("world"))
    joined = Shlex_.join(parts)
    assert isinstance(joined, Str)
    assert joined._value == "echo hello world"


def test_join_quotes_when_needed() -> None:
    parts = List(Str("echo"), Str("hello world"))
    joined = Shlex_.join(parts)
    # Either single-quoted or escaped — shlex picks safe quoting.
    assert "hello world" in joined._value or "hello\\ world" in joined._value


def test_quote_escapes_special_chars() -> None:
    result = Shlex_.quote(Str("hello world"))
    assert isinstance(result, Str)
    assert " " not in result._value or result._value.startswith("'")


def test_quote_safe_string_unchanged() -> None:
    result = Shlex_.quote(Str("safe-text"))
    assert result == Str("safe-text")


# --- Shlex class ---


def test_shlex_class_iterates_tokens() -> None:
    lex = Shlex(Str("echo hello world"))
    tokens = list(lex)
    assert tokens == [Str("echo"), Str("hello"), Str("world")]


def test_shlex_class_get_token_eof() -> None:
    lex = Shlex(Str("a"))
    assert lex.get_token() == Str("a")
    assert lex.get_token() is none


def test_shlex_class_lineno() -> None:
    lex = Shlex(Str("a\nb\nc"))
    list(lex)
    # After consuming all tokens, lineno reflects the file position.
    assert lex.lineno >= Int(1)


# --- Interpreter integration ---


def test_shlex_split_reachable_via_interpreter() -> None:
    Interpreter().run_source('shlex.split("echo hi").len().print()')


def test_Shlex_class_reachable_via_interpreter() -> None:
    Interpreter().run_source('Shlex("a b c").get_token().print()')


def test_punctuation_chars_reads_back_resolved_set() -> None:
    assert Shlex(Str("a;b")).punctuation_chars == Str("")
    enabled = Shlex(Str("a;b"), punctuation_chars=true)
    assert enabled.punctuation_chars.includes(Str(";")) is true
