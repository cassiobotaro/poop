from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.fnmatch import Fnmatch
from poop.types.list import List
from poop.types.string import Str


def test_fnmatch_matching() -> None:
    assert Fnmatch.fnmatch(Str("foo.py"), Str("*.py")) is true


def test_fnmatch_not_matching() -> None:
    assert Fnmatch.fnmatch(Str("foo.txt"), Str("*.py")) is false


def test_fnmatchcase_case_sensitive_match() -> None:
    assert Fnmatch.fnmatchcase(Str("FOO.PY"), Str("*.PY")) is true


def test_fnmatchcase_case_sensitive_no_match() -> None:
    # On a case-insensitive default-fnmatch we'd say true; fnmatchcase respects case.
    assert Fnmatch.fnmatchcase(Str("foo.py"), Str("*.PY")) is false


def test_filter_keeps_matching() -> None:
    names = List(Str("a.py"), Str("b.txt"), Str("c.py"))
    result = Fnmatch.filter(names, Str("*.py"))
    assert isinstance(result, List)
    assert result.len()._value == 2


def test_filter_with_empty_list() -> None:
    result = Fnmatch.filter(List(), Str("*.py"))
    assert isinstance(result, List)
    assert result.len()._value == 0


def test_translate_returns_regex_str() -> None:
    result = Fnmatch.translate(Str("*.py"))
    assert isinstance(result, Str)
    assert ".py" in result._value


def test_fnmatch_reachable_via_interpreter() -> None:
    Interpreter().run_source('fnmatch.fnmatch("foo.py", "*.py").print()')
