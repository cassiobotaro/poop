from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tarfile import TarFile, Tarfile, TarInfo


def _make_source_tree(tmp_path: _PyPath) -> _PyPath:
    src = tmp_path / "source"
    src.mkdir()
    (src / "a.txt").write_text("alpha")
    (src / "b.txt").write_text("beta")
    sub = src / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("gamma")
    return src


# --- TarFile.open / add / extract ---


def test_open_write_and_inspect(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "out.tar"

    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("source"))

    with TarFile.open(Path(Str(str(archive)))) as tar:
        names = tar.getnames()

    assert isinstance(names, List)
    names_list = [n._value if isinstance(n, Str) else n for n in names]
    assert "source/a.txt" in names_list
    assert "source/sub/c.txt" in names_list


def test_getmembers_returns_tarinfos(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "members.tar"

    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("source"))

    with TarFile.open(Path(Str(str(archive)))) as tar:
        members = tar.getmembers()

    assert isinstance(members, List)
    first = members.at(Int(0))
    assert isinstance(first, TarInfo)
    assert isinstance(first.name, Str)
    assert isinstance(first.size, Int)


def test_getmember_by_name(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "by-name.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src / "a.txt"))), arcname=Str("a.txt"))

    with TarFile.open(Path(Str(str(archive)))) as tar:
        info = tar.getmember(Str("a.txt"))

    assert isinstance(info, TarInfo)
    assert info.name == Str("a.txt")


def test_extractall_round_trip(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "ext.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("source"))

    out = tmp_path / "out"
    out.mkdir()
    with TarFile.open(Path(Str(str(archive)))) as tar:
        assert tar.extractall(Path(Str(str(out)))) is none

    assert (out / "source" / "a.txt").read_text() == "alpha"
    assert (out / "source" / "sub" / "c.txt").read_text() == "gamma"


def test_extract_single_member(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "single.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src / "a.txt"))), arcname=Str("a.txt"))

    out = tmp_path / "single_out"
    out.mkdir()
    with TarFile.open(Path(Str(str(archive)))) as tar:
        assert tar.extract(Str("a.txt"), Path(Str(str(out)))) is none

    assert (out / "a.txt").read_text() == "alpha"


def test_gzip_compressed_tar(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "out.tar.gz"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w:gz")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("source"))
    with TarFile.open(Path(Str(str(archive))), mode=Str("r:gz")) as tar:
        names = tar.getnames()
    assert names.includes(Str("source/a.txt"))


def test_is_tarfile_true(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "yes.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("s"))
    assert TarFile.is_tarfile(Path(Str(str(archive)))) is True


def test_is_tarfile_false(tmp_path: _PyPath) -> None:
    not_tar = tmp_path / "no.tar"
    not_tar.write_text("not a tar")
    assert TarFile.is_tarfile(Path(Str(str(not_tar)))) is False


def test_read_error_on_invalid(tmp_path: _PyPath) -> None:
    not_tar = tmp_path / "no.tar"
    not_tar.write_text("nope")
    with pytest.raises(Tarfile.ReadError):
        TarFile.open(Path(Str(str(not_tar))))


def test_list_writes_to_stdout(
    tmp_path: _PyPath, capsys: pytest.CaptureFixture[str]
) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "list.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("source"))
    with TarFile.open(Path(Str(str(archive)))) as tar:
        assert tar.list() is none
    captured = capsys.readouterr().out
    assert "source/a.txt" in captured


# --- TarInfo properties ---


def test_tarinfo_properties(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "props.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src / "a.txt"))), arcname=Str("a.txt"))
    with TarFile.open(Path(Str(str(archive)))) as tar:
        info = tar.getmember(Str("a.txt"))
    assert info.name == Str("a.txt")
    assert info.size == Int(5)
    assert isinstance(info.mtime, Int)
    assert isinstance(info.mode, Int)
    assert isinstance(info.uid, Int)
    assert isinstance(info.gid, Int)
    assert isinstance(info.uname, Str)
    assert isinstance(info.gname, Str)
    assert info.is_file is True
    assert info.is_dir is False
    assert info.is_symlink is False
    assert info.is_link is False


# --- Constants / errors ---


def test_format_constants_are_ints() -> None:
    assert isinstance(Tarfile.DEFAULT_FORMAT, Int)
    assert isinstance(Tarfile.USTAR_FORMAT, Int)
    assert isinstance(Tarfile.GNU_FORMAT, Int)
    assert isinstance(Tarfile.PAX_FORMAT, Int)


def test_encoding_constant_is_str() -> None:
    assert isinstance(Tarfile.ENCODING, Str)


def test_filter_callables_exposed() -> None:
    assert callable(Tarfile.data_filter)
    assert callable(Tarfile.tar_filter)
    assert callable(Tarfile.fully_trusted_filter)


def test_error_classes_exposed() -> None:
    assert issubclass(Tarfile.ReadError, Tarfile.TarError)
    assert issubclass(Tarfile.HeaderError, Tarfile.TarError)
    assert issubclass(Tarfile.FilterError, Tarfile.TarError)


# --- Extra coverage ---


def test_extract_with_tarinfo_member(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "by-info.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src / "a.txt"))), arcname=Str("a.txt"))

    out = tmp_path / "by-info-out"
    out.mkdir()
    with TarFile.open(Path(Str(str(archive)))) as tar:
        info = tar.getmember(Str("a.txt"))
        tar.extract(info, Path(Str(str(out))))

    assert (out / "a.txt").read_text() == "alpha"


def test_extractall_with_members(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "members.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src))), arcname=Str("source"))

    out = tmp_path / "members-out"
    out.mkdir()
    with TarFile.open(Path(Str(str(archive)))) as tar:
        info = tar.getmember(Str("source/a.txt"))
        tar.extractall(Path(Str(str(out))), members=List(info))

    assert (out / "source" / "a.txt").read_text() == "alpha"


def test_extractall_rejects_str_members(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "bad.tar"
    with TarFile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src / "a.txt"))), arcname=Str("a.txt"))

    out = tmp_path / "bad-out"
    out.mkdir()
    with TarFile.open(Path(Str(str(archive)))) as tar:
        with pytest.raises(TypeError):
            tar.extractall(Path(Str(str(out))), members=List(Str("a.txt")))


# --- Namespace alias ---


def test_namespace_open_delegates(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "ns.tar"
    with Tarfile.open(Path(Str(str(archive))), mode=Str("w")) as tar:
        tar.add(Path(Str(str(src / "a.txt"))), arcname=Str("a.txt"))
    with Tarfile.open(Path(Str(str(archive)))) as tar:
        assert tar.getnames() == List(Str("a.txt"))


# --- Interpreter integration ---


def test_tarfile_reachable_via_interpreter(tmp_path: _PyPath) -> None:
    src = _make_source_tree(tmp_path)
    archive = tmp_path / "i.tar"
    source_path = src / "a.txt"
    Interpreter().run_source(
        f't = TarFile.open(Path("{archive}"), "w")\n'
        f't.add(Path("{source_path}"), "a.txt")\n'
        "t.close()\n"
        f'r = TarFile.open(Path("{archive}"))\n'
        "r.getnames().print()\n"
        "r.close()"
    )
