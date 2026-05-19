from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.zipfile import ZipFile, Zipfile, ZipInfo

# --- ZipFile read/write ---


def test_zipfile_write_and_read_back(tmp_path: _PyPath) -> None:
    archive = tmp_path / "out.zip"
    z = ZipFile(Path(Str(str(archive))), mode=Str("w"))
    z.writestr(Str("a.txt"), Bytes(b"alpha"))
    z.writestr(Str("b.txt"), Bytes(b"beta"))
    z.close()

    reader = ZipFile(Path(Str(str(archive))))
    assert reader.read(Str("a.txt")) == Bytes(b"alpha")
    assert reader.read(Str("b.txt")) == Bytes(b"beta")
    reader.close()


def test_zipfile_namelist(tmp_path: _PyPath) -> None:
    archive = tmp_path / "names.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("x.txt"), Bytes(b"x"))
        z.writestr(Str("y.txt"), Bytes(b"y"))
    with ZipFile(Path(Str(str(archive)))) as z:
        names = z.namelist()
    assert isinstance(names, List)
    assert names == List(Str("x.txt"), Str("y.txt"))


def test_zipfile_infolist_returns_zipinfo(tmp_path: _PyPath) -> None:
    archive = tmp_path / "info.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("a"), Bytes(b"data"))
    with ZipFile(Path(Str(str(archive)))) as z:
        infos = z.infolist()
    assert isinstance(infos, List)
    first = infos.at(Int(0))
    assert isinstance(first, ZipInfo)
    assert first.filename == Str("a")
    assert first.file_size == Int(4)


def test_zipinfo_properties(tmp_path: _PyPath) -> None:
    archive = tmp_path / "props.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("file"), Bytes(b"hello"))
    with ZipFile(Path(Str(str(archive)))) as z:
        info = z.getinfo(Str("file"))
    assert isinstance(info, ZipInfo)
    assert info.filename == Str("file")
    assert info.file_size == Int(5)
    assert isinstance(info.compress_size, Int)
    assert isinstance(info.compress_type, Int)
    assert isinstance(info.date_time, Tuple)
    assert info.date_time.len() == Int(6)
    assert isinstance(info.CRC, Int)
    assert isinstance(info.is_dir, bool)


def test_zipfile_write_from_disk(tmp_path: _PyPath) -> None:
    source = tmp_path / "source.txt"
    source.write_text("payload")
    archive = tmp_path / "out.zip"

    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.write(Path(Str(str(source))), arcname=Str("renamed.txt"))

    with ZipFile(Path(Str(str(archive)))) as z:
        assert z.read(Str("renamed.txt")) == Bytes(b"payload")


def test_zipfile_extract_single_member(tmp_path: _PyPath) -> None:
    archive = tmp_path / "ext.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("f.txt"), Bytes(b"payload"))

    extract_dir = tmp_path / "out"
    extract_dir.mkdir()
    with ZipFile(Path(Str(str(archive)))) as z:
        path = z.extract(Str("f.txt"), Path(Str(str(extract_dir))))
    assert isinstance(path, Path)
    assert (extract_dir / "f.txt").read_text() == "payload"


def test_zipfile_extractall(tmp_path: _PyPath) -> None:
    archive = tmp_path / "all.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("a.txt"), Bytes(b"A"))
        z.writestr(Str("b.txt"), Bytes(b"B"))

    extract_dir = tmp_path / "all"
    extract_dir.mkdir()
    with ZipFile(Path(Str(str(archive)))) as z:
        assert z.extractall(Path(Str(str(extract_dir)))) is none
    assert (extract_dir / "a.txt").read_bytes() == b"A"
    assert (extract_dir / "b.txt").read_bytes() == b"B"


def test_zipfile_extractall_members_filter(tmp_path: _PyPath) -> None:
    archive = tmp_path / "filter.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("a.txt"), Bytes(b"A"))
        z.writestr(Str("b.txt"), Bytes(b"B"))

    extract_dir = tmp_path / "filt"
    extract_dir.mkdir()
    with ZipFile(Path(Str(str(archive)))) as z:
        z.extractall(Path(Str(str(extract_dir))), members=List(Str("a.txt")))
    assert (extract_dir / "a.txt").exists()
    assert not (extract_dir / "b.txt").exists()


def test_zipfile_testzip_clean(tmp_path: _PyPath) -> None:
    archive = tmp_path / "clean.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("ok.txt"), Bytes(b"x"))
    with ZipFile(Path(Str(str(archive)))) as z:
        result = z.testzip()
    assert isinstance(result, NoneClass)


def test_zipfile_with_deflated_compression(tmp_path: _PyPath) -> None:
    archive = tmp_path / "deflated.zip"
    with ZipFile(
        Path(Str(str(archive))),
        mode=Str("w"),
        compression=Zipfile.ZIP_DEFLATED,
    ) as z:
        z.writestr(Str("data"), Bytes(b"x" * 1000))
    with ZipFile(Path(Str(str(archive)))) as z:
        assert z.read(Str("data")) == Bytes(b"x" * 1000)
        info = z.getinfo(Str("data"))
    # Deflated should be smaller than the original.
    assert info.compress_size._value < info.file_size._value


def test_zipfile_setpassword_round_trip(tmp_path: _PyPath) -> None:
    archive = tmp_path / "pwd.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("secret"), Bytes(b"hi"))

    with ZipFile(Path(Str(str(archive)))) as z:
        assert z.setpassword(Bytes(b"pwd")) is none


# --- is_zipfile / errors / constants ---


def test_is_zipfile_true(tmp_path: _PyPath) -> None:
    archive = tmp_path / "x.zip"
    with ZipFile(Path(Str(str(archive))), mode=Str("w")) as z:
        z.writestr(Str("a"), Bytes(b"a"))
    assert Zipfile.is_zipfile(Path(Str(str(archive)))) is true


def test_is_zipfile_false(tmp_path: _PyPath) -> None:
    not_zip = tmp_path / "no.zip"
    not_zip.write_text("not a zip")
    assert Zipfile.is_zipfile(Path(Str(str(not_zip)))) is false


def test_bad_zip_file_raises(tmp_path: _PyPath) -> None:
    not_zip = tmp_path / "no.zip"
    not_zip.write_text("not a zip")
    with pytest.raises(Zipfile.BadZipFile):
        ZipFile(Path(Str(str(not_zip))))


def test_compression_constants_are_ints() -> None:
    assert isinstance(Zipfile.ZIP_STORED, Int)
    assert isinstance(Zipfile.ZIP_DEFLATED, Int)
    assert isinstance(Zipfile.ZIP_BZIP2, Int)
    assert isinstance(Zipfile.ZIP_LZMA, Int)


def test_error_classes_exposed() -> None:
    assert issubclass(Zipfile.LargeZipFile, Exception)


# --- Interpreter integration ---


def test_zipfile_reachable_via_interpreter(tmp_path: _PyPath) -> None:
    archive = tmp_path / "i.zip"
    src = (
        f'z = ZipFile(Path("{archive}"), "w")\n'
        'z.writestr("a", b"data")\n'
        "z.close()\n"
        f'r = ZipFile(Path("{archive}"))\n'
        'r.read("a").print()\n'
        "r.close()"
    )
    Interpreter().run_source(src)


def test_zipfile_namespace_constants_via_interpreter() -> None:
    Interpreter().run_source("zipfile.ZIP_DEFLATED.print()")
