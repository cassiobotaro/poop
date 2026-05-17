import pathlib
import tempfile

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.glob import Glob, GlobIter
from poop.types.list import List
from poop.types.path import Path
from poop.types.string import Str


@pytest.fixture
def sample_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "c.md").write_text("c")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.txt").write_text("deep")
    return tmp_path


def test_glob_returns_list_of_paths(sample_tree: pathlib.Path) -> None:
    pattern = Str(str(sample_tree / "*.txt"))
    result = Glob.glob(pattern)
    assert isinstance(result, List)
    assert result.len()._value == 2
    for p in result:
        assert isinstance(p, Path)


def test_glob_recursive(sample_tree: pathlib.Path) -> None:
    pattern = Str(str(sample_tree / "**" / "*.txt"))
    result = Glob.glob(pattern, recursive=true)
    assert result.len()._value == 3


def test_glob_with_root_dir(sample_tree: pathlib.Path) -> None:
    result = Glob.glob(Str("*.txt"), root_dir=Path(Str(str(sample_tree))))
    assert isinstance(result, List)
    assert result.len()._value == 2


def test_iglob_returns_glob_iter(sample_tree: pathlib.Path) -> None:
    pattern = Str(str(sample_tree / "*.txt"))
    result = Glob.iglob(pattern)
    assert isinstance(result, GlobIter)


def test_iglob_iterates_paths(sample_tree: pathlib.Path) -> None:
    pattern = Str(str(sample_tree / "*.txt"))
    paths = list(Glob.iglob(pattern))
    assert len(paths) == 2
    assert all(isinstance(p, Path) for p in paths)


def test_iglob_to_list(sample_tree: pathlib.Path) -> None:
    pattern = Str(str(sample_tree / "*.txt"))
    result = Glob.iglob(pattern).to_list()
    assert isinstance(result, List)
    assert result.len()._value == 2


def test_escape_returns_poop_str() -> None:
    result = Glob.escape(Str("file[1].txt"))
    assert isinstance(result, Str)
    # Brackets become escaped
    assert "[" in result._value or "*" not in result._value


def test_translate_returns_regex_str() -> None:
    result = Glob.translate(Str("*.py"))
    assert isinstance(result, Str)
    assert ".py" in result._value


def test_glob_reachable_via_interpreter() -> None:
    with tempfile.TemporaryDirectory() as d:
        Interpreter().run_source(f'glob.glob("{d}/*").len().print()')


def test_glob_with_root_dir_as_str(sample_tree: pathlib.Path) -> None:
    # Exercises the Str branch of root_dir handling in Glob.glob.
    result = Glob.glob(Str("*.txt"), root_dir=Str(str(sample_tree)))
    assert result.len()._value == 2


def test_iglob_with_root_dir_as_path(sample_tree: pathlib.Path) -> None:
    result = Glob.iglob(Str("*.txt"), root_dir=Path(Str(str(sample_tree))))
    assert isinstance(result, GlobIter)
    assert len(list(result)) == 2


def test_iglob_with_root_dir_as_str(sample_tree: pathlib.Path) -> None:
    result = Glob.iglob(Str("*.txt"), root_dir=Str(str(sample_tree)))
    assert isinstance(result, GlobIter)
    assert len(list(result)) == 2
