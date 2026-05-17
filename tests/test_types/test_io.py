from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.io import IO, BytesIO, StringIO
from poop.types.none import none
from poop.types.string import Str

# --- StringIO ---


def test_stringio_constructs_empty() -> None:
    assert isinstance(StringIO(), StringIO)


def test_stringio_constructs_with_initial() -> None:
    s = StringIO(Str("hello"))
    assert s.getvalue() == Str("hello")


def test_stringio_constructs_with_newline() -> None:
    assert isinstance(StringIO(Str(""), Str("\n")), StringIO)


def test_stringio_write_and_read() -> None:
    s = StringIO()
    assert s.write(Str("abc")) == Int(3)
    s.seek(Int(0))
    assert s.read() == Str("abc")


def test_stringio_read_with_size() -> None:
    s = StringIO(Str("hello"))
    assert s.read(Int(3)) == Str("hel")


def test_stringio_readline() -> None:
    s = StringIO(Str("a\nb\n"))
    assert s.readline() == Str("a\n")


def test_stringio_readline_with_size() -> None:
    s = StringIO(Str("hello"))
    assert s.readline(Int(3)) == Str("hel")


def test_stringio_tell() -> None:
    s = StringIO()
    s.write(Str("abc"))
    assert s.tell() == Int(3)


def test_stringio_seek() -> None:
    s = StringIO(Str("hello"))
    assert s.seek(Int(2)) == Int(2)


def test_stringio_seek_with_whence() -> None:
    s = StringIO(Str("hello"))
    assert s.seek(Int(0), IO.SEEK_END) == Int(5)


def test_stringio_truncate() -> None:
    s = StringIO(Str("hello"))
    assert s.truncate(Int(2)) == Int(2)
    assert s.getvalue() == Str("he")


def test_stringio_close_returns_none() -> None:
    s = StringIO()
    assert s.close() is none


def test_stringio_context_manager() -> None:
    with StringIO(Str("body")) as s:
        assert s.getvalue() == Str("body")


# --- BytesIO ---


def test_bytesio_constructs_empty() -> None:
    assert isinstance(BytesIO(), BytesIO)


def test_bytesio_constructs_with_initial() -> None:
    b = BytesIO(Bytes(b"data"))
    assert b.getvalue() == Bytes(b"data")


def test_bytesio_write_and_read() -> None:
    b = BytesIO()
    assert b.write(Bytes(b"x")) == Int(1)
    b.seek(Int(0))
    assert b.read() == Bytes(b"x")


def test_bytesio_read_with_size() -> None:
    b = BytesIO(Bytes(b"hello"))
    assert b.read(Int(3)) == Bytes(b"hel")


def test_bytesio_readline() -> None:
    b = BytesIO(Bytes(b"a\nb\n"))
    assert b.readline() == Bytes(b"a\n")


def test_bytesio_readline_with_size() -> None:
    b = BytesIO(Bytes(b"hello"))
    assert b.readline(Int(3)) == Bytes(b"hel")


def test_bytesio_tell_and_seek() -> None:
    b = BytesIO(Bytes(b"hello"))
    b.seek(Int(2))
    assert b.tell() == Int(2)


def test_bytesio_seek_whence() -> None:
    b = BytesIO(Bytes(b"hello"))
    assert b.seek(Int(0), IO.SEEK_END) == Int(5)


def test_bytesio_truncate() -> None:
    b = BytesIO(Bytes(b"hello"))
    assert b.truncate(Int(2)) == Int(2)
    assert b.getvalue() == Bytes(b"he")


def test_bytesio_close_returns_none() -> None:
    b = BytesIO()
    assert b.close() is none


def test_bytesio_context_manager() -> None:
    with BytesIO(Bytes(b"x")) as b:
        assert b.getvalue() == Bytes(b"x")


# --- IO namespace constants ---


def test_io_constants_are_ints() -> None:
    for attr in ("SEEK_SET", "SEEK_CUR", "SEEK_END", "DEFAULT_BUFFER_SIZE"):
        assert isinstance(getattr(IO, attr), Int)


def test_io_class_refs() -> None:
    assert IO.StringIO is StringIO
    assert IO.BytesIO is BytesIO


def test_io_error_classes() -> None:
    assert issubclass(IO.UnsupportedOperation, Exception)
    assert issubclass(IO.BlockingIOError, Exception)


# --- Interpreter integration ---


def test_io_via_interpreter() -> None:
    Interpreter().run_source(
        "buf = StringIO()\nbuf.write('hi')\nbuf.getvalue().print()"
    )
