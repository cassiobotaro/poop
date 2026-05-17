import os
from pathlib import Path as _PyPath

from poop.interpreter import Interpreter
from poop.types.boolean import false
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tempfile import (
    NamedTemporaryFile,
    SpooledTemporaryFile,
    TempfileNamespace,
    TemporaryDirectory,
    TemporaryFile,
)
from poop.types.tuple import Tuple

# --- mkstemp / mkdtemp ---


def test_mkstemp_returns_tuple_of_fd_and_path(tmp_path: _PyPath) -> None:
    result = TempfileNamespace.mkstemp(dir=Path(Str(str(tmp_path))))
    assert isinstance(result, Tuple)
    fd = result.at(Int(0))
    path = result.at(Int(1))
    assert isinstance(fd, Int)
    assert isinstance(path, Path)
    assert path.exists()
    os.close(fd._value)


def test_mkstemp_respects_prefix_and_suffix(tmp_path: _PyPath) -> None:
    result = TempfileNamespace.mkstemp(
        suffix=Str(".dat"),
        prefix=Str("test_"),
        dir=Path(Str(str(tmp_path))),
    )
    fd = result.at(Int(0))
    path = result.at(Int(1))
    assert isinstance(fd, Int)
    assert isinstance(path, Path)
    name = str(path._path)
    assert name.endswith(".dat")
    assert "test_" in name
    os.close(fd._value)


def test_mkdtemp_creates_directory(tmp_path: _PyPath) -> None:
    path = TempfileNamespace.mkdtemp(dir=Path(Str(str(tmp_path))))
    assert isinstance(path, Path)
    assert path.exists()


# --- tempdir metadata ---


def test_gettempdir_returns_path() -> None:
    result = TempfileNamespace.gettempdir()
    assert isinstance(result, Path)
    assert result.exists()


def test_gettempprefix_returns_str() -> None:
    assert isinstance(TempfileNamespace.gettempprefix(), Str)


def test_gettempdirb_returns_bytes() -> None:
    assert isinstance(TempfileNamespace.gettempdirb(), Bytes)


def test_gettempprefixb_returns_bytes() -> None:
    assert isinstance(TempfileNamespace.gettempprefixb(), Bytes)


# --- tempdir / set_tempdir ---


def test_set_tempdir_round_trip(tmp_path: _PyPath) -> None:
    TempfileNamespace.tempdir = Path(Str(str(tmp_path)))
    try:
        assert TempfileNamespace.tempdir == Path(Str(str(tmp_path)))
    finally:
        TempfileNamespace.tempdir = none


def test_tempdir_default_is_none() -> None:
    TempfileNamespace.tempdir = none
    assert TempfileNamespace.tempdir is none


# --- TemporaryDirectory ---


def test_temporary_directory_creates_and_cleans_up() -> None:
    td = TemporaryDirectory()
    name = td.name
    assert isinstance(name, Path)
    assert name.exists()
    td.cleanup()
    assert not name.exists()


def test_temporary_directory_with_context_manager() -> None:
    captured: list[Path] = []
    with TemporaryDirectory() as path:
        assert isinstance(path, Path)
        assert path.exists()
        captured.append(path)
    assert not captured[0].exists()


def test_temporary_directory_with_prefix(tmp_path: _PyPath) -> None:
    td = TemporaryDirectory(prefix=Str("poop_"), dir=Path(Str(str(tmp_path))))
    try:
        assert "poop_" in str(td.name._path)
    finally:
        td.cleanup()


# --- TemporaryFile ---


def test_temporary_file_write_read_round_trip() -> None:
    tf = TemporaryFile()
    try:
        assert tf.write(Bytes(b"hello")) == Int(5)
        tf.seek(Int(0))
        assert tf.read() == Bytes(b"hello")
    finally:
        tf.close()


def test_temporary_file_context_manager() -> None:
    with TemporaryFile() as tf:
        assert tf.write(Bytes(b"abc")) == Int(3)


def test_temporary_file_text_mode() -> None:
    tf = TemporaryFile(mode=Str("w+"))
    try:
        tf.write(Str("hello"))
        tf.seek(Int(0))
        assert tf.read() == Str("hello")
    finally:
        tf.close()


# --- NamedTemporaryFile ---


def test_named_temporary_file_name_is_path() -> None:
    ntf = NamedTemporaryFile(delete=false)
    try:
        assert isinstance(ntf.name, Path)
        assert ntf.name.exists()
    finally:
        ntf.close()
        # Manual cleanup since delete=false.
        ntf.name._path.unlink(missing_ok=True)


def test_named_temporary_file_default_delete_removes_on_close() -> None:
    ntf = NamedTemporaryFile()
    name = ntf.name
    ntf.close()
    assert not name.exists()


def test_named_temporary_file_context_manager() -> None:
    with NamedTemporaryFile() as ntf:
        ntf.write(Bytes(b"ctx"))
        ntf.seek(Int(0))
        assert ntf.read() == Bytes(b"ctx")


def test_named_temporary_file_tell_and_flush() -> None:
    ntf = NamedTemporaryFile()
    try:
        ntf.write(Bytes(b"abcd"))
        assert ntf.tell() == Int(4)
        assert ntf.flush() is none
    finally:
        ntf.close()


# --- SpooledTemporaryFile ---


def test_spooled_temporary_file_in_memory() -> None:
    sf = SpooledTemporaryFile(max_size=Int(1024))
    try:
        sf.write(Bytes(b"in-memory"))
        sf.seek(Int(0))
        assert sf.read() == Bytes(b"in-memory")
    finally:
        sf.close()


def test_spooled_temporary_file_rollover() -> None:
    sf = SpooledTemporaryFile(max_size=Int(1024))
    try:
        sf.write(Bytes(b"data"))
        assert sf.rollover() is none
    finally:
        sf.close()


def test_spooled_temporary_file_context_manager() -> None:
    with SpooledTemporaryFile(max_size=Int(8)) as sf:
        sf.write(Bytes(b"small"))


# --- Interpreter integration ---


def test_tempfile_gettempdir_reachable_via_interpreter() -> None:
    Interpreter().run_source("tempfile.gettempdir().exists().print()")


def test_TemporaryDirectory_reachable_via_interpreter() -> None:
    Interpreter().run_source(
        "td = TemporaryDirectory()\ntd.name.exists().print()\ntd.cleanup()"
    )
