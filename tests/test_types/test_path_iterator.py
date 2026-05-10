import pathlib as _pathlib

import pytest

from poop.types.boolean import false, true
from poop.types.filter import Filter
from poop.types.map import Map
from poop.types.none import none
from poop.types.path import Path
from poop.types.path_iterator import PathIterator


@pytest.fixture
def tree(tmp_path: _pathlib.Path) -> _pathlib.Path:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("bb", encoding="utf-8")
    (tmp_path / "c.md").write_text("ccc", encoding="utf-8")
    return tmp_path


def test_iter_yields_path_instances(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    items = list(it)
    assert len(items) == 3
    assert all(isinstance(p, Path) for p in items)


def test_next_advances(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    first = it.next()
    second = it.next()
    assert isinstance(first, Path)
    assert isinstance(second, Path)
    assert first._path != second._path


def test_next_raises_stopiteration_on_exhaustion(tree: _pathlib.Path) -> None:
    it = PathIterator([])
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_exhaustion(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    list(it)
    assert list(it) == []


def test_do_consumes(tree: _pathlib.Path) -> None:
    seen: list[Path] = []
    result = PathIterator(tree.iterdir()).do(lambda p: seen.append(p))
    assert result is none
    assert len(seen) == 3


def test_map_returns_map_lazy(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    m = it.map(lambda p: p.suffix)
    assert isinstance(m, Map)


def test_filter_returns_filter_lazy(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    f = it.filter(lambda p: p.suffix._value == ".txt")
    assert isinstance(f, Filter)
    names = sorted(p._path.name for p in f)
    assert names == ["a.txt", "b.txt"]


def test_all_predicate(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    assert it.all(lambda p: p.is_file()) is true


def test_any_predicate(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    assert it.any(lambda p: p.suffix._value == ".md") is true
    it2 = PathIterator(tree.iterdir())
    assert it2.any(lambda p: p.suffix._value == ".rs") is false


def test_find_returns_first_match(tree: _pathlib.Path) -> None:
    it = PathIterator(tree.iterdir())
    found = it.find(lambda p: p.suffix._value == ".md")
    assert isinstance(found, Path)
    assert found._path.name == "c.md"


def test_str_repr() -> None:
    it = PathIterator([])
    assert str(it) == "<path_iterator>"
    assert repr(it) == "<path_iterator>"
