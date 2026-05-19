"""
Safe config lookup — `if_none`/`if_not_none` chain

`Dict.get(missing_key)` returns `none` (Smalltalk's `nil`), not a
KeyError. Combined with `if_not_none(block)` (executes only when the
value is present) and `if_none(block)` (executes only when absent),
nested optional access becomes a flat chain. Each step keeps the same
shape: object responds to messages, even when "object" is `none`.

Compare with the procedural Python version:

    db = config.get("database")
    if db is None:
        return "localhost"
    host = db.get("host")
    if host is None:
        return "localhost"
    return host

POOP forbids `is None` against polymorphic types — `none` is itself a
NoneClass instance answering `if_none`/`if_not_none` like any other
object. No branch, no special case.

Smalltalk (nil-aware ifNotNil: / ifNil:):
    | host |
    host := (config at: 'database')
        ifNotNil: [:db | db at: 'host']
        ifNil:    ['localhost'].
"""


class ConfigReader:
    def __init__(self, config):
        self._config = config

    def database_host(self, default):
        return (
            self._config.get("database")
            .if_not_none(lambda db: db.get("host"))
            .if_none(lambda: default)
        )


full = {"database": {"host": "db.example.com", "port": 5432}}
missing_host = {"database": {"port": 5432}}
missing_db = {"server": {"workers": 4}}

ConfigReader(full).database_host("localhost").print()
ConfigReader(missing_host).database_host("localhost").print()
ConfigReader(missing_db).database_host("localhost").print()
