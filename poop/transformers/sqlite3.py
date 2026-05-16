from poop.types.sqlite3 import Connection, Cursor, Row, Sqlite3

NAMESPACE: dict[str, object] = {
    "sqlite3": Sqlite3,
    "Connection": Connection,
    "Cursor": Cursor,
    "Row": Row,
}
