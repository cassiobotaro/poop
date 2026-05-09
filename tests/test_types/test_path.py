from pathlib import Path as NativePath

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str


def _path(path: NativePath) -> Path:
    return Path(Str(str(path)))


def test_ctor_is_idempotent(tmp_path: NativePath) -> None:
    inner = _path(tmp_path / "a.txt")
    outer = Path(inner)
    assert outer._path == inner._path


def test_write_and_read_text_roundtrip(tmp_path: NativePath) -> None:
    file_path = _path(tmp_path / "hello.txt")
    assert file_path.write_text(Str("hello")) == Int(5)
    assert file_path.read_text() == Str("hello")


def test_write_and_read_bytes_roundtrip(tmp_path: NativePath) -> None:
    file_path = _path(tmp_path / "hello.bin")
    assert file_path.write_bytes(Bytes(b"abc")) == Int(3)
    assert file_path.read_bytes() == Bytes(b"abc")


def test_exists_is_file_is_dir(tmp_path: NativePath) -> None:
    file_path = _path(tmp_path / "a.txt")
    dir_path = _path(tmp_path / "d")

    assert file_path.exists() is false
    dir_path.mkdir()
    assert dir_path.exists() is true
    assert dir_path.is_dir() is true
    assert dir_path.is_file() is false

    file_path.write_text(Str("x"))
    assert file_path.exists() is true
    assert file_path.is_file() is true
    assert file_path.is_dir() is false


def test_mkdir_touch_unlink_rmdir_return_none(tmp_path: NativePath) -> None:
    dir_path = _path(tmp_path / "dir")
    file_path = _path(tmp_path / "dir" / "a.txt")

    assert dir_path.mkdir() is none
    assert file_path.touch() is none
    assert file_path.unlink() is none
    assert dir_path.rmdir() is none


def test_joinpath_and_truediv(tmp_path: NativePath) -> None:
    base = _path(tmp_path)
    assert base.joinpath(Str("a"), Str("b")).as_posix().includes(Str("/a/b")) is true
    assert (base / Str("x")).name == Str("x")


def test_properties(tmp_path: NativePath) -> None:
    p = _path(tmp_path / "folder" / "file.txt")

    assert p.name == Str("file.txt")
    assert p.stem == Str("file")
    assert p.suffix == Str(".txt")
    assert p.parent.name == Str("folder")
    assert p.parts.len() > Int(0)
    assert p.parents.len() > Int(0)


def test_iterdir_glob_rglob(tmp_path: NativePath) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.py").write_text("b", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.py").write_text("c", encoding="utf-8")

    base = _path(tmp_path)
    assert base.iterdir().len() == Int(3)
    assert base.glob(Str("*.py")).len() == Int(1)
    assert base.rglob(Str("*.py")).len() == Int(2)


def test_resolve_absolute_relative_to(tmp_path: NativePath) -> None:
    base = _path(tmp_path)
    child = _path(tmp_path / "x.txt")

    assert child.absolute().is_absolute() is true
    assert child.resolve().is_absolute() is true
    assert child.relative_to(base) == Path(Str("x.txt"))


def test_rename_and_replace(tmp_path: NativePath) -> None:
    src = _path(tmp_path / "a.txt")
    dst = _path(tmp_path / "b.txt")
    other = _path(tmp_path / "c.txt")

    src.write_text(Str("a"))
    renamed = src.rename(dst)
    assert renamed.name == Str("b.txt")

    other.write_text(Str("c"))
    replaced = renamed.replace(other)
    assert replaced.name == Str("c.txt")


def test_classmethods_and_repr() -> None:
    assert Path.cwd().exists() is true
    assert Path.home().exists() is true
    assert repr(Path.cwd()) == str(Path.cwd())
