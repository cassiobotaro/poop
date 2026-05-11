import pathlib as _pathlib

import pytest

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.map import Map
from poop.types.none import none
from poop.types.path import Path
from poop.types.path_iterator import PathIterator
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- ctor / idempotency ---


def test_ctor_from_str() -> None:
    p = Path(Str("foo.txt"))
    assert p._path == _pathlib.Path("foo.txt")


def test_ctor_idempotent() -> None:
    inner = Path(Str("foo.txt"))
    outer = Path(inner)
    assert outer._path == inner._path


def test_from_pathlib_skips_init() -> None:
    p = Path._from_pathlib(_pathlib.Path("a/b/c"))
    assert p._path == _pathlib.Path("a/b/c")


# --- classmethods ---


def test_cwd_returns_path() -> None:
    assert isinstance(Path.cwd(), Path)
    assert Path.cwd()._path == _pathlib.Path.cwd()


def test_home_returns_path() -> None:
    assert isinstance(Path.home(), Path)
    assert Path.home()._path == _pathlib.Path.home()


# --- I/O ---


def test_read_text_returns_str(tmp_path: _pathlib.Path) -> None:
    f = tmp_path / "x.txt"
    f.write_text("hello", encoding="utf-8")
    result = Path(Str(str(f))).read_text()
    assert isinstance(result, Str)
    assert result._value == "hello"


def test_write_text_returns_int_byte_count(tmp_path: _pathlib.Path) -> None:
    f = tmp_path / "x.txt"
    written = Path(Str(str(f))).write_text(Str("hello"))
    assert isinstance(written, Int)
    assert written._value == 5
    assert f.read_text(encoding="utf-8") == "hello"


def test_read_bytes_returns_bytes(tmp_path: _pathlib.Path) -> None:
    f = tmp_path / "x.bin"
    f.write_bytes(b"\x00\x01\x02")
    result = Path(Str(str(f))).read_bytes()
    assert isinstance(result, Bytes)
    assert result._value == b"\x00\x01\x02"


def test_write_bytes_returns_int_byte_count(tmp_path: _pathlib.Path) -> None:
    f = tmp_path / "x.bin"
    written = Path(Str(str(f))).write_bytes(Bytes(b"\x00\x01\x02"))
    assert isinstance(written, Int)
    assert written._value == 3
    assert f.read_bytes() == b"\x00\x01\x02"


# --- predicates ---


def test_exists_true(tmp_path: _pathlib.Path) -> None:
    assert Path(Str(str(tmp_path))).exists() is true


def test_exists_false(tmp_path: _pathlib.Path) -> None:
    assert Path(Str(str(tmp_path / "nope"))).exists() is false


def test_is_file(tmp_path: _pathlib.Path) -> None:
    f = tmp_path / "x"
    f.write_text("y", encoding="utf-8")
    assert Path(Str(str(f))).is_file() is true
    assert Path(Str(str(tmp_path))).is_file() is false


def test_is_dir(tmp_path: _pathlib.Path) -> None:
    assert Path(Str(str(tmp_path))).is_dir() is true
    f = tmp_path / "x"
    f.write_text("y", encoding="utf-8")
    assert Path(Str(str(f))).is_dir() is false


def test_is_symlink(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "target"
    target.write_text("x", encoding="utf-8")
    link = tmp_path / "link"
    link.symlink_to(target)
    assert Path(Str(str(link))).is_symlink() is true
    assert Path(Str(str(target))).is_symlink() is false


def test_is_absolute() -> None:
    assert Path(Str("/abs/path")).is_absolute() is true
    assert Path(Str("rel/path")).is_absolute() is false


# --- mutations returning none ---


def test_mkdir_creates_dir(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "new"
    result = Path(Str(str(target))).mkdir()
    assert result is none
    assert target.is_dir()


def test_mkdir_with_parents_and_exist_ok(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "a" / "b" / "c"
    Path(Str(str(target))).mkdir(parents=true, exist_ok=true)
    Path(Str(str(target))).mkdir(parents=true, exist_ok=true)  # idempotent
    assert target.is_dir()


def test_rmdir_removes_empty_dir(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "doomed"
    target.mkdir()
    result = Path(Str(str(target))).rmdir()
    assert result is none
    assert not target.exists()


def test_unlink_removes_file(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "doomed"
    target.write_text("x", encoding="utf-8")
    result = Path(Str(str(target))).unlink()
    assert result is none
    assert not target.exists()


def test_unlink_missing_ok(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "ghost"
    Path(Str(str(target))).unlink(missing_ok=true)


def test_unlink_missing_raises_without_flag(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "ghost"
    with pytest.raises(FileNotFoundError):
        Path(Str(str(target))).unlink()


def test_touch_creates_empty_file(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "fresh"
    result = Path(Str(str(target))).touch()
    assert result is none
    assert target.is_file()
    assert target.read_text(encoding="utf-8") == ""


def test_mkdir_accepts_poop_none_kwargs(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "new"
    Path(Str(str(target))).mkdir(mode=none, parents=none, exist_ok=none)
    assert target.is_dir()


def test_touch_accepts_poop_none_kwargs(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "fresh"
    Path(Str(str(target))).touch(mode=none, exist_ok=none)
    assert target.is_file()


def test_unlink_accepts_poop_none_kwarg(tmp_path: _pathlib.Path) -> None:
    target = tmp_path / "doomed"
    target.write_text("x", encoding="utf-8")
    Path(Str(str(target))).unlink(missing_ok=none)
    assert not target.exists()


# --- methods returning Path ---


def test_resolve_returns_path(tmp_path: _pathlib.Path) -> None:
    p = Path(Str(str(tmp_path))).resolve()
    assert isinstance(p, Path)
    assert p._path == tmp_path.resolve()


def test_absolute_returns_path() -> None:
    p = Path(Str("rel")).absolute()
    assert isinstance(p, Path)
    assert p._path.is_absolute()


def test_rename_returns_new_path(tmp_path: _pathlib.Path) -> None:
    src = tmp_path / "src"
    src.write_text("x", encoding="utf-8")
    dst = tmp_path / "dst"
    result = Path(Str(str(src))).rename(Str(str(dst)))
    assert isinstance(result, Path)
    assert result._path == dst
    assert dst.read_text(encoding="utf-8") == "x"


def test_rename_accepts_path_target(tmp_path: _pathlib.Path) -> None:
    src = tmp_path / "src"
    src.write_text("x", encoding="utf-8")
    dst = tmp_path / "dst"
    result = Path(Str(str(src))).rename(Path(Str(str(dst))))
    assert result._path == dst


def test_replace_overwrites_target(tmp_path: _pathlib.Path) -> None:
    src = tmp_path / "src"
    src.write_text("new", encoding="utf-8")
    dst = tmp_path / "dst"
    dst.write_text("old", encoding="utf-8")
    Path(Str(str(src))).replace(Str(str(dst)))
    assert dst.read_text(encoding="utf-8") == "new"


def test_joinpath_combines_segments() -> None:
    p = Path(Str("a")).joinpath(Str("b"), Str("c"))
    assert p._path == _pathlib.Path("a/b/c")


def test_joinpath_accepts_path_segments() -> None:
    p = Path(Str("a")).joinpath(Path(Str("b")))
    assert p._path == _pathlib.Path("a/b")


def test_with_name_replaces_basename() -> None:
    p = Path(Str("dir/file.txt")).with_name(Str("other.md"))
    assert p._path == _pathlib.Path("dir/other.md")


def test_with_suffix_replaces_extension() -> None:
    p = Path(Str("dir/file.txt")).with_suffix(Str(".md"))
    assert p._path == _pathlib.Path("dir/file.md")


def test_with_stem_replaces_stem() -> None:
    p = Path(Str("dir/file.txt")).with_stem(Str("other"))
    assert p._path == _pathlib.Path("dir/other.txt")


def test_relative_to_returns_relative() -> None:
    p = Path(Str("/a/b/c")).relative_to(Str("/a"))
    assert p._path == _pathlib.Path("b/c")


# --- Str-returning conversions ---


def test_as_posix() -> None:
    result = Path(Str("a/b")).as_posix()
    assert isinstance(result, Str)
    assert result._value == "a/b"


def test_as_uri() -> None:
    result = Path(Str("/abs/path")).as_uri()
    assert isinstance(result, Str)
    assert result._value.startswith("file://")


# --- iterdir / glob / rglob ---


def test_iterdir_returns_path_iterator(tmp_path: _pathlib.Path) -> None:
    (tmp_path / "a").write_text("", encoding="utf-8")
    (tmp_path / "b").write_text("", encoding="utf-8")
    it = Path(Str(str(tmp_path))).iterdir()
    assert isinstance(it, PathIterator)
    items = list(it)
    assert len(items) == 2
    assert all(isinstance(p, Path) for p in items)


def test_glob_returns_map(tmp_path: _pathlib.Path) -> None:
    (tmp_path / "a.txt").write_text("", encoding="utf-8")
    (tmp_path / "b.md").write_text("", encoding="utf-8")
    it = Path(Str(str(tmp_path))).glob(Str("*.txt"))
    assert isinstance(it, Map)
    items = [p for p in it if isinstance(p, Path)]
    assert sorted(p._path.name for p in items) == ["a.txt"]


def test_rglob_recursive_returns_map(tmp_path: _pathlib.Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "x.txt").write_text("", encoding="utf-8")
    (tmp_path / "y.txt").write_text("", encoding="utf-8")
    it = Path(Str(str(tmp_path))).rglob(Str("*.txt"))
    assert isinstance(it, Map)
    items = [p for p in it if isinstance(p, Path)]
    assert sorted(p._path.name for p in items) == ["x.txt", "y.txt"]


# --- properties ---


def test_name_property() -> None:
    result = Path(Str("dir/file.txt")).name
    assert isinstance(result, Str)
    assert result._value == "file.txt"


def test_stem_property() -> None:
    assert Path(Str("dir/file.txt")).stem._value == "file"


def test_suffix_property() -> None:
    assert Path(Str("dir/file.txt")).suffix._value == ".txt"


def test_parts_property() -> None:
    result = Path(Str("a/b/c")).parts
    assert isinstance(result, Tuple)
    items = [s for s in result if isinstance(s, Str)]
    assert [s._value for s in items] == ["a", "b", "c"]


def test_parent_property() -> None:
    result = Path(Str("a/b/c")).parent
    assert isinstance(result, Path)
    assert result._path == _pathlib.Path("a/b")


def test_parents_property() -> None:
    result = Path(Str("a/b/c")).parents
    assert isinstance(result, Tuple)
    items = [p for p in result if isinstance(p, Path)]
    assert [p._path for p in items] == [
        _pathlib.Path("a/b"),
        _pathlib.Path("a"),
        _pathlib.Path("."),
    ]


# --- operators ---


def test_truediv_with_str() -> None:
    p = Path(Str("dir")) / Str("file.txt")
    assert isinstance(p, Path)
    assert p._path == _pathlib.Path("dir/file.txt")


def test_truediv_with_path() -> None:
    p = Path(Str("dir")) / Path(Str("file.txt"))
    assert p._path == _pathlib.Path("dir/file.txt")


def test_eq_same_path() -> None:
    assert (Path(Str("a")) == Path(Str("a"))) is true


def test_eq_different_path() -> None:
    assert (Path(Str("a")) == Path(Str("b"))) is false


def test_eq_non_path() -> None:
    assert (Path(Str("a")) == Str("a")) is false


def test_ne() -> None:
    assert (Path(Str("a")) != Path(Str("b"))) is true
    assert (Path(Str("a")) != Path(Str("a"))) is false


def test_lt_le_gt_ge() -> None:
    a = Path(Str("a"))
    b = Path(Str("b"))
    assert (a < b) is true
    assert (b < a) is false
    assert (a <= a) is true
    assert (b > a) is true
    assert (a >= a) is true


def test_hash_matches_pathlib() -> None:
    assert hash(Path(Str("a/b"))) == hash(_pathlib.Path("a/b"))


def test_hash_equal_paths_equal_hash() -> None:
    assert hash(Path(Str("a"))) == hash(Path(Str("a")))


# --- str / repr ---


def test_str() -> None:
    assert str(Path(Str("a/b"))) == "a/b"


def test_repr() -> None:
    assert repr(Path(Str("a/b"))) == "Path('a/b')"
