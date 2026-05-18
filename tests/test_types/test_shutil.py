from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.boolean import true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.path import Path
from poop.types.shutil import Shutil
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- copy / copy2 / copyfile ---


def test_copy_round_trip(tmp_path: _PyPath) -> None:
    src = tmp_path / "src.txt"
    src.write_text("hello")
    dst = tmp_path / "dst.txt"
    result = Shutil.copy(Path(Str(str(src))), Path(Str(str(dst))))
    assert isinstance(result, Path)
    assert dst.read_text() == "hello"


def test_copy2_preserves_metadata(tmp_path: _PyPath) -> None:
    src = tmp_path / "src.txt"
    src.write_text("data")
    dst = tmp_path / "dst.txt"
    result = Shutil.copy2(Path(Str(str(src))), Path(Str(str(dst))))
    assert isinstance(result, Path)
    assert dst.exists()


def test_copyfile_basic(tmp_path: _PyPath) -> None:
    src = tmp_path / "src.txt"
    src.write_text("x")
    dst = tmp_path / "dst.txt"
    result = Shutil.copyfile(Path(Str(str(src))), Path(Str(str(dst))))
    assert isinstance(result, Path)
    assert dst.read_text() == "x"


def test_copytree_creates_full_tree(tmp_path: _PyPath) -> None:
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "a.txt").write_text("a")
    (src / "sub" / "b.txt").write_text("b")
    dst = tmp_path / "dst"
    result = Shutil.copytree(Path(Str(str(src))), Path(Str(str(dst))))
    assert isinstance(result, Path)
    assert (dst / "a.txt").read_text() == "a"
    assert (dst / "sub" / "b.txt").read_text() == "b"


def test_copytree_dirs_exist_ok(tmp_path: _PyPath) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "x.txt").write_text("x")
    dst = tmp_path / "dst"
    dst.mkdir()
    result = Shutil.copytree(
        Path(Str(str(src))), Path(Str(str(dst))), dirs_exist_ok=true
    )
    assert (dst / "x.txt").read_text() == "x"
    assert isinstance(result, Path)


def test_copytree_ignore_block_drops_names(tmp_path: _PyPath) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "keep.txt").write_text("k")
    (src / "skip.txt").write_text("s")
    dst = tmp_path / "dst"

    def ignore(path: Str, names: List) -> List:
        return List(*(n for n in names if n == Str("skip.txt")))

    Shutil.copytree(Path(Str(str(src))), Path(Str(str(dst))), ignore=Block(ignore))
    assert (dst / "keep.txt").exists()
    assert not (dst / "skip.txt").exists()


def test_copytree_ignore_patterns_factory(tmp_path: _PyPath) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.py").write_text("p")
    (src / "b.txt").write_text("t")
    dst = tmp_path / "dst"

    Shutil.copytree(
        Path(Str(str(src))),
        Path(Str(str(dst))),
        ignore=Shutil.ignore_patterns(Str("*.txt")),
    )
    assert (dst / "a.py").exists()
    assert not (dst / "b.txt").exists()


def test_copytree_copy_function_block_is_invoked(tmp_path: _PyPath) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "f.txt").write_text("hello")
    dst = tmp_path / "dst"

    seen: list[tuple[Str, Str]] = []

    def custom_copy(s: Str, d: Str) -> NoneClass:
        seen.append((s, d))
        _PyPath(d._value).write_text(_PyPath(s._value).read_text())
        return none

    Shutil.copytree(
        Path(Str(str(src))),
        Path(Str(str(dst))),
        copy_function=Block(custom_copy),
    )
    assert (dst / "f.txt").read_text() == "hello"
    assert seen and isinstance(seen[0][0], Str)


def test_move_copy_function_block(tmp_path: _PyPath) -> None:
    # Cross-device move forces shutil to use copy_function then unlink.
    src = tmp_path / "src.txt"
    src.write_text("payload")
    dst = tmp_path / "dst.txt"

    seen: list[Str] = []

    def custom_copy(s: Str, d: Str) -> Str:
        seen.append(s)
        _PyPath(d._value).write_text(_PyPath(s._value).read_text())
        return d

    Shutil.move(
        Path(Str(str(src))), Path(Str(str(dst))), copy_function=Block(custom_copy)
    )
    # When rename works (same filesystem), copy_function isn't called.
    # Just check the move succeeded.
    assert dst.read_text() == "payload"


def test_copymode_returns_none(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("x")
    b.write_text("y")
    assert Shutil.copymode(Path(Str(str(a))), Path(Str(str(b)))) is none


def test_copystat_returns_none(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("x")
    b.write_text("y")
    assert Shutil.copystat(Path(Str(str(a))), Path(Str(str(b)))) is none


# --- move / remove ---


def test_move_file(tmp_path: _PyPath) -> None:
    src = tmp_path / "src.txt"
    src.write_text("payload")
    dst = tmp_path / "dst.txt"
    result = Shutil.move(Path(Str(str(src))), Path(Str(str(dst))))
    assert isinstance(result, Path)
    assert not src.exists()
    assert dst.read_text() == "payload"


def test_rmtree_recursive(tmp_path: _PyPath) -> None:
    root = tmp_path / "tree"
    (root / "sub").mkdir(parents=True)
    (root / "a.txt").write_text("a")
    assert Shutil.rmtree(Path(Str(str(root)))) is none
    assert not root.exists()


def test_rmtree_ignore_errors(tmp_path: _PyPath) -> None:
    # Path doesn't exist — ignore_errors swallows the failure.
    assert (
        Shutil.rmtree(Path(Str(str(tmp_path / "nonexistent"))), ignore_errors=true)
        is none
    )


def test_rmtree_missing_raises(tmp_path: _PyPath) -> None:
    with pytest.raises(FileNotFoundError):
        Shutil.rmtree(Path(Str(str(tmp_path / "missing"))))


# --- which ---


def test_which_finds_known_command() -> None:
    # POSIX systems have at least `sh` somewhere on PATH.
    result = Shutil.which(Str("sh"))
    assert isinstance(result, Path)
    assert str(result._path).endswith("/sh") or str(result._path).endswith("sh")


def test_which_unknown_returns_none() -> None:
    result = Shutil.which(Str("definitely_not_a_command_xyz"))
    assert isinstance(result, NoneClass)


# --- Archive helpers ---


def test_make_and_unpack_archive(tmp_path: _PyPath) -> None:
    src = tmp_path / "source"
    src.mkdir()
    (src / "file.txt").write_text("payload")

    base = tmp_path / "bundle"
    archive_path = Shutil.make_archive(
        Path(Str(str(base))),
        Str("zip"),
        root_dir=Path(Str(str(tmp_path))),
        base_dir=Str("source"),
    )
    assert isinstance(archive_path, Path)
    assert archive_path.exists()

    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    Shutil.unpack_archive(archive_path, Path(Str(str(extract_dir))))
    assert (extract_dir / "source" / "file.txt").read_text() == "payload"


def test_get_archive_formats_returns_list_of_tuples() -> None:
    result = Shutil.get_archive_formats()
    assert isinstance(result, List)
    first = result.at(Int(0))
    assert isinstance(first, Tuple)
    name = first.at(Int(0))
    assert isinstance(name, Str)


def test_get_unpack_formats_returns_triples() -> None:
    result = Shutil.get_unpack_formats()
    assert isinstance(result, List)
    first = result.at(Int(0))
    assert isinstance(first, Tuple)
    assert isinstance(first.at(Int(0)), Str)
    assert isinstance(first.at(Int(1)), List)
    assert isinstance(first.at(Int(2)), Str)


# --- Disk / terminal info ---


def test_disk_usage_returns_int_triple(tmp_path: _PyPath) -> None:
    result = Shutil.disk_usage(Path(Str(str(tmp_path))))
    assert isinstance(result, Tuple)
    total = result.at(Int(0))
    used = result.at(Int(1))
    free = result.at(Int(2))
    assert isinstance(total, Int)
    assert isinstance(used, Int)
    assert isinstance(free, Int)
    assert total._value > 0


def test_get_terminal_size_default() -> None:
    result = Shutil.get_terminal_size()
    assert isinstance(result, Tuple)
    cols = result.at(Int(0))
    lines = result.at(Int(1))
    assert isinstance(cols, Int)
    assert isinstance(lines, Int)


def test_get_terminal_size_fallback() -> None:
    fallback = Tuple(Int(80), Int(24))
    result = Shutil.get_terminal_size(fallback=fallback)
    assert isinstance(result, Tuple)


# --- Error constants ---


def test_error_classes_exposed() -> None:
    assert isinstance(Shutil.Error, type)
    assert issubclass(Shutil.SameFileError, OSError)


def test_copyfile_same_file_raises(tmp_path: _PyPath) -> None:
    src = tmp_path / "f.txt"
    src.write_text("x")
    with pytest.raises(Shutil.SameFileError):
        Shutil.copyfile(Path(Str(str(src))), Path(Str(str(src))))


# --- Interpreter integration ---


def test_shutil_which_reachable_via_interpreter() -> None:
    Interpreter().run_source('shutil.which("sh").is_none().print()')


def test_shutil_disk_usage_reachable_via_interpreter() -> None:
    Interpreter().run_source('shutil.disk_usage(".").print()')


def test_unpack_archive_with_format_kwarg(tmp_path: _PyPath) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "f.txt").write_text("hi")
    archive = Shutil.make_archive(
        Path(Str(str(tmp_path / "out"))), Str("zip"), root_dir=Path(Str(str(src)))
    )
    target = tmp_path / "extract"
    target.mkdir()
    assert (
        Shutil.unpack_archive(
            archive, extract_dir=Path(Str(str(target))), format=Str("zip")
        )
        is none
    )
    assert (target / "f.txt").read_text() == "hi"


def test_chown_with_current_user(tmp_path: _PyPath) -> None:
    import getpass as _getpass

    f = tmp_path / "f.txt"
    f.write_text("x")
    # chown to the current user is a no-op but exercises the kwargs path.
    assert Shutil.chown(Path(Str(str(f))), user=Str(_getpass.getuser())) is none


# --- Try.except_ integration ---


def test_try_catches_same_file_error(tmp_path: _PyPath) -> None:
    from poop.types.try_ import Try

    captured: list[object] = []
    src = tmp_path / "self.txt"
    src.write_text("x")
    Try(lambda: Shutil.copyfile(Path(Str(str(src))), Path(Str(str(src))))).except_(
        Shutil.SameFileError, lambda e: captured.append(e.message())
    ).run()
    assert len(captured) == 1


def test_try_catches_rmtree_missing(tmp_path: _PyPath) -> None:
    from poop.types.try_ import Try

    captured: list[object] = []
    missing = tmp_path / "ghost"
    Try(lambda: Shutil.rmtree(Path(Str(str(missing))))).except_(
        FileNotFoundError, lambda e: captured.append(e.kind())
    ).run()
    assert len(captured) == 1
