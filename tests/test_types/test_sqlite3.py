import sqlite3 as _sqlite3

import pytest

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.sqlite3 import Connection, Cursor, Row, Sqlite3
from poop.types.string import Str
from poop.types.tuple import Tuple


def _make_db() -> Connection:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE users(id INTEGER, name TEXT)"))
    con.execute(Str("INSERT INTO users VALUES (?, ?)"), Tuple(Int(1), Str("Alice")))
    con.execute(Str("INSERT INTO users VALUES (?, ?)"), Tuple(Int(2), Str("Bob")))
    return con


def test_connect_returns_connection() -> None:
    assert isinstance(Sqlite3.connect(Str(":memory:")), Connection)


def test_connection_cursor() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    assert isinstance(con.cursor(), Cursor)


def test_connection_execute_returns_cursor() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    assert isinstance(con.execute(Str("SELECT 1")), Cursor)


def test_connection_execute_with_params() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT name FROM users WHERE id = ?"), Tuple(Int(1)))
    row = cur.fetchone()
    assert isinstance(row, Tuple)
    assert row.at(Int(0)) == Str("Alice")


def test_connection_executemany() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(x INTEGER)"))
    con.executemany(
        Str("INSERT INTO t VALUES (?)"),
        List(Tuple(Int(1)), Tuple(Int(2)), Tuple(Int(3))),
    )
    rows = con.execute(Str("SELECT * FROM t")).fetchall()
    assert isinstance(rows, List)
    assert rows.len() == Int(3)


def test_connection_executescript() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.executescript(Str("CREATE TABLE t1(x INTEGER); CREATE TABLE t2(y TEXT);"))
    tables = con.execute(
        Str("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    ).fetchall()
    assert tables.len() == Int(2)


def test_connection_commit_rollback() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(x INTEGER)"))
    assert con.commit() is none
    assert con.rollback() is none


def test_connection_close() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    assert con.close() is none


def test_connection_interrupt() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    assert con.interrupt() is none


def test_connection_iterdump() -> None:
    con = _make_db()
    dump = con.iterdump()
    assert isinstance(dump, List)
    assert dump.len()._value > 0


def test_connection_backup() -> None:
    src = _make_db()
    src.commit()
    dst = Sqlite3.connect(Str(":memory:"))
    assert src.backup(dst) is none
    rows = dst.execute(Str("SELECT * FROM users")).fetchall()
    assert rows.len() == Int(2)


def test_connection_context_manager() -> None:
    with Sqlite3.connect(Str(":memory:")) as con:
        assert isinstance(con, Connection)
        con.execute(Str("CREATE TABLE t(x INTEGER)"))


def test_cursor_fetchone_after_query() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT * FROM users ORDER BY id"))
    row = cur.fetchone()
    assert isinstance(row, Tuple)
    assert row.at(Int(0)) == Int(1)
    assert row.at(Int(1)) == Str("Alice")


def test_cursor_fetchone_no_more_rows_returns_none() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(x INTEGER)"))
    cur = con.execute(Str("SELECT * FROM t"))
    assert cur.fetchone() is none


def test_cursor_fetchmany() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT * FROM users"))
    out = cur.fetchmany(Int(1))
    assert isinstance(out, List)
    assert out.len() == Int(1)


def test_cursor_fetchall() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT * FROM users"))
    out = cur.fetchall()
    assert isinstance(out, List)
    assert out.len() == Int(2)


def test_cursor_rowcount() -> None:
    con = _make_db()
    cur = con.execute(Str("INSERT INTO users VALUES (?, ?)"), Tuple(Int(3), Str("C")))
    assert isinstance(cur.rowcount, Int)


def test_cursor_lastrowid() -> None:
    con = _make_db()
    cur = con.execute(Str("INSERT INTO users VALUES (?, ?)"), Tuple(Int(3), Str("C")))
    assert isinstance(cur.lastrowid, Int)


def test_cursor_description_after_select() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT id, name FROM users"))
    desc = cur.description
    assert isinstance(desc, Tuple)
    first = desc.at(Int(0))
    assert isinstance(first, Tuple)
    assert first.at(Int(0)) == Str("id")


def test_cursor_arraysize() -> None:
    con = _make_db()
    cur = con.cursor()
    assert isinstance(cur.arraysize, Int)


def test_cursor_close() -> None:
    con = _make_db()
    cur = con.cursor()
    assert cur.close() is none


def test_cursor_iteration() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT id FROM users ORDER BY id"))
    ids = [row.at(Int(0))._value for row in cur]
    assert ids == [1, 2]


def test_row_construction_and_access() -> None:
    row = Row(("id", "name"), (1, "Alice"))
    assert row.at(Int(0)) == Int(1)
    assert row.at(Str("name")) == Str("Alice")
    assert row.len() == Int(2)


def test_row_keys_values() -> None:
    row = Row(("id", "name"), (1, "Alice"))
    keys = row.keys()
    assert isinstance(keys, Tuple)
    assert keys.at(Int(0)) == Str("id")
    values = row.values()
    assert values.at(Int(1)) == Str("Alice")


def test_sqlite3_constants() -> None:
    assert Sqlite3.sqlite_version == Str(_sqlite3.sqlite_version)
    assert Sqlite3.PARSE_DECLTYPES == Int(_sqlite3.PARSE_DECLTYPES)
    assert Sqlite3.PARSE_COLNAMES == Int(_sqlite3.PARSE_COLNAMES)


def test_sqlite3_error_classes_exposed() -> None:
    assert Sqlite3.Warning is _sqlite3.Warning
    assert Sqlite3.Error is _sqlite3.Error
    assert Sqlite3.InterfaceError is _sqlite3.InterfaceError
    assert Sqlite3.DatabaseError is _sqlite3.DatabaseError
    assert Sqlite3.DataError is _sqlite3.DataError
    assert Sqlite3.OperationalError is _sqlite3.OperationalError
    assert Sqlite3.IntegrityError is _sqlite3.IntegrityError
    assert Sqlite3.InternalError is _sqlite3.InternalError
    assert Sqlite3.ProgrammingError is _sqlite3.ProgrammingError
    assert Sqlite3.NotSupportedError is _sqlite3.NotSupportedError


def test_sqlite3_class_attributes() -> None:
    assert Sqlite3.Connection is Connection
    assert Sqlite3.Cursor is Cursor
    assert Sqlite3.Row is Row


def test_operational_error_raises_through_poop() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    with pytest.raises(_sqlite3.OperationalError):
        con.execute(Str("SELECT * FROM nonexistent_table"))


def test_integrity_error_raises_through_poop() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(id INTEGER PRIMARY KEY)"))
    con.execute(Str("INSERT INTO t VALUES (1)"))
    with pytest.raises(_sqlite3.IntegrityError):
        con.execute(Str("INSERT INTO t VALUES (1)"))


def test_sqlite3_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["sqlite3"] is Sqlite3
    assert DEFAULT_NAMESPACE["Connection"] is Connection
    assert DEFAULT_NAMESPACE["Cursor"] is Cursor
    assert DEFAULT_NAMESPACE["Row"] is Row


def test_sqlite3_reachable_via_interpreter() -> None:
    Interpreter().run_source(
        'sqlite3.connect(":memory:").execute("SELECT 1").fetchone().at(0).print()'
    )


def test_connect_with_uri_and_check_same_thread() -> None:
    con = Sqlite3.connect(Str(":memory:"), check_same_thread=false)
    assert isinstance(con, Connection)


def test_value_wrapping_returns_poop_types() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(i INTEGER, f REAL, s TEXT, b BLOB)"))
    con.execute(
        Str("INSERT INTO t VALUES (?, ?, ?, ?)"),
        Tuple(Int(1), Int(0), Str("hi"), Str("dummy")),
    )
    row = con.execute(Str("SELECT * FROM t")).fetchone()
    assert isinstance(row, Tuple)


# --- Coverage: value-wrap branches, connect kwargs, Path arg, executemany,
#     executescript, lastrowid ---


def test_wrap_value_null_int_float_bytes() -> None:
    from poop.types.bytes import Bytes
    from poop.types.float import Float

    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(n, i INTEGER, f REAL, b BLOB)"))
    con.execute(
        Str("INSERT INTO t VALUES (?, ?, ?, ?)"),
        Tuple(none, Int(5), Float(2.5), Bytes(b"abc")),
    )
    row = con.execute(Str("SELECT * FROM t")).fetchone()
    assert isinstance(row, Tuple)
    assert row.at(Int(0)) is none
    assert row.at(Int(1)) == Int(5)
    assert isinstance(row.at(Int(2)), Float)
    assert row.at(Int(3)) == Bytes(b"abc")


def test_unwrap_value_bool_and_none() -> None:
    from poop.types.boolean import true

    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(b, n)"))
    con.execute(Str("INSERT INTO t VALUES (?, ?)"), Tuple(true, none))
    row = con.execute(Str("SELECT * FROM t")).fetchone()
    assert isinstance(row, Tuple)


def test_unwrap_params_with_list_form() -> None:
    con = _make_db()
    cur = con.execute(Str("SELECT name FROM users WHERE id = ?"), List(Int(2)))
    row = cur.fetchone()
    assert isinstance(row, Tuple)
    assert row.at(Int(0)) == Str("Bob")


def test_executemany_and_executescript() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE x(n INTEGER)"))
    cur = con.cursor()
    cur.executemany(Str("INSERT INTO x VALUES (?)"), List(Tuple(Int(1)), Tuple(Int(2))))
    rows = con.execute(Str("SELECT n FROM x ORDER BY n")).fetchall()
    assert rows.len() == Int(2)
    # executescript runs multiple statements in one call.
    cur.executescript(Str("DELETE FROM x; INSERT INTO x VALUES (42);"))
    rows = con.execute(Str("SELECT n FROM x")).fetchall()
    assert rows.len() == Int(1)


def test_cursor_lastrowid_returns_int_after_insert() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(id INTEGER PRIMARY KEY, n TEXT)"))
    cur = con.execute(Str("INSERT INTO t(n) VALUES ('a')"))
    assert isinstance(cur.lastrowid, Int)


def test_connect_with_path_arg(tmp_path: object) -> None:
    from poop.types.path import Path

    p = Path(Str(str(tmp_path) + "/foo.sqlite"))  # type: ignore[unresolved-attribute]
    con = Sqlite3.connect(p)
    assert isinstance(con, Connection)
    con.close()


def test_connect_with_full_kwargs() -> None:
    from poop.types.boolean import true
    from poop.types.float import Float

    con = Sqlite3.connect(
        Str(":memory:"),
        timeout=Float(1.0),
        detect_types=Int(0),
        isolation_level=Str("DEFERRED"),
        cached_statements=Int(50),
        uri=true,
    )
    assert isinstance(con, Connection)


def test_row_len_dunder() -> None:
    row = Row(("a", "b"), (1, 2))
    assert len(row) == 2


# --- Try.except_ integration ---


def test_try_catches_operational_error() -> None:
    from poop.types.try_ import Try

    captured: list[object] = []
    con = Sqlite3.connect(Str(":memory:"))
    Try(lambda: con.execute(Str("SELECT * FROM no_such_table"))).except_(
        Sqlite3.OperationalError, lambda e: captured.append(e.message())
    ).run()
    assert len(captured) == 1
    assert isinstance(captured[0], Str)


def test_try_catches_integrity_error() -> None:
    from poop.types.try_ import Try

    captured: list[object] = []
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE t(id INTEGER PRIMARY KEY)"))
    con.execute(Str("INSERT INTO t VALUES (1)"))
    Try(lambda: con.execute(Str("INSERT INTO t VALUES (1)"))).except_(
        Sqlite3.IntegrityError, lambda e: captured.append(e.kind())
    ).run()
    assert len(captured) == 1


# --- Bridge consumers: callbacks ---


def test_create_function_routes_through_bridge() -> None:
    seen: list[Str] = []

    def shout(s: Str) -> Str:
        seen.append(s)
        return Str(s._value.upper())

    con = Sqlite3.connect(Str(":memory:"))
    con.create_function(Str("shout"), Int(1), Block(shout))
    cur = con.execute(Str("SELECT shout('hi')"))
    row = cur.fetchone()
    assert isinstance(row, Tuple)
    assert row.at(Int(0)) == Str("HI")
    assert seen == [Str("hi")]


def test_create_function_deterministic_kwarg() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.create_function(Str("two"), Int(0), Block(lambda: Int(2)), deterministic=true)
    cur = con.execute(Str("SELECT two()"))
    assert cur.fetchone().at(Int(0)) == Int(2)


def test_create_collation_routes_through_bridge() -> None:
    # Sort strings by length, ties by codepoint.
    def by_len(a: Str, b: Str) -> Int:
        la, lb = len(a._value), len(b._value)
        if la != lb:
            return Int(-1) if la < lb else Int(1)
        if a._value == b._value:
            return Int(0)
        return Int(-1) if a._value < b._value else Int(1)

    con = Sqlite3.connect(Str(":memory:"))
    con.create_collation(Str("BYLEN"), Block(by_len))
    con.execute(Str("CREATE TABLE w(s TEXT)"))
    for word in ("ccc", "a", "bb"):
        con.execute(Str("INSERT INTO w VALUES (?)"), Tuple(Str(word)))
    cur = con.execute(Str("SELECT s FROM w ORDER BY s COLLATE BYLEN"))
    assert [r.at(Int(0)) for r in cur.fetchall()._items] == [
        Str("a"),
        Str("bb"),
        Str("ccc"),
    ]


def test_create_collation_none_removes_registration() -> None:
    con = Sqlite3.connect(Str(":memory:"))
    con.create_collation(Str("MYCOLL"), Block(lambda a, b: Int(0)))
    # Removing it should not raise.
    assert con.create_collation(Str("MYCOLL"), None) is none


def test_register_adapter_routes_through_bridge() -> None:
    from poop.types.object import Object

    class Money(Object):
        __slots__ = ("cents",)

        def __init__(self, cents: int) -> None:
            self.cents = cents

    def adapt(m: Money) -> Int:
        # The bridge wraps the Money into POOP (opaque pass-through),
        # then we return a POOP Int — bridge unwraps to int for storage.
        return Int(m.cents)

    Sqlite3.register_adapter(Money, Block(adapt))
    con = Sqlite3.connect(Str(":memory:"))
    con.execute(Str("CREATE TABLE p(amount INTEGER)"))
    con.execute(Str("INSERT INTO p VALUES (?)"), Tuple(Money(199)))
    cur = con.execute(Str("SELECT amount FROM p"))
    assert cur.fetchone().at(Int(0)) == Int(199)


def test_register_converter_routes_through_bridge() -> None:
    def revert(raw: Bytes) -> Str:
        # Bridge wraps raw bytes to POOP Bytes, hand back a POOP Str.
        return Str(raw._value.decode("utf-8")[::-1])

    Sqlite3.register_converter(Str("REVERSED"), Block(revert))
    con = Sqlite3.connect(Str(":memory:"), detect_types=Sqlite3.PARSE_DECLTYPES)
    con.execute(Str("CREATE TABLE r(v REVERSED)"))
    con.execute(Str("INSERT INTO r VALUES (?)"), Tuple(Str("abc")))
    cur = con.execute(Str("SELECT v FROM r"))
    assert cur.fetchone().at(Int(0)) == Str("cba")
